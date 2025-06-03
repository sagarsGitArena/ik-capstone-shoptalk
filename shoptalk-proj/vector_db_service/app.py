from flask import Flask, request, jsonify, render_template
import faiss
import numpy as np
import cupy  # CuPy to support GPU operations
import os
import sys
import pandas as pd
import json
import logging
from sentence_transformers import SentenceTransformer
import requests
import mlflow



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
print(f'faiss: app.py - PATH: {sys.path}')

from utils.s3_utils import download_file_from_s3, delete_file_from_s3, upload_file_to_s3
from config import BUCKET_NAME, S3_DATA_FILE_PATH, LOCAL_DATA_DIR
from config import FAISS_LOCAL_DB_STORE, FAISS_METADATA_JSON_FILE, FAISS_INDEX_BIN_FILE, FAISS_METADATA_JSON_FILE_S3_OBJECT_KEY, FAISS_INDEX_FILE_S3_OBJECT_KEY, FAISS_INDEX_PATH, FAISS_METADATA_PATH, FAISS_INDEX_TO_ITEM_ID_JSON_FILE, FAISS_INDEX_TO_ITEM_ID_JSON_FILE_PATH
    

app = Flask(__name__)


# Initialize FAISS index to use GPU
dimension = 128  # Example dimensionality

# Move FAISS index to GPU
res = faiss.StandardGpuResources()  # Initialize GPU resources
index_cpu = faiss.IndexFlatL2(dimension)  # Create index on CPU
index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)  # Move index to GPU

# Load FAISS index and metadata
def load_faiss_index():
    local_index_bin_file_path = os.path.join(FAISS_LOCAL_DB_STORE, FAISS_INDEX_BIN_FILE)
    local_json_metadata_file_path = os.path.join(FAISS_LOCAL_DB_STORE, FAISS_METADATA_JSON_FILE)

    # Load FAISS index
    index = faiss.read_index(local_index_bin_file_path)

    # Load metadata
    with open(local_json_metadata_file_path, "r") as f:
        metadata = json.load(f)

    return index, metadata

# Load CSV metadata
def load_metadata():
    metadata_csv_path = 'shoptalk-proj/data/us_listings_images_merged_captioned_v1.csv'
    try:
        return pd.read_csv(metadata_csv_path)
    except FileNotFoundError:
        print(f"Error: The file at {metadata_csv_path} was not found.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return None
    except pd.errors.ParserError:
        print("Error: The file could not be parsed.")
        return None

# Load FAISS index and metadata
def load_faiss_index_and_metadata():
    # Load FAISS index
    index = faiss.read_index('shoptalk-proj/vector_database/faiss_db/faiss_index.bin')
    
    # Load metadata
    with open('shoptalk-proj/vector_database/faiss_db/faiss_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    return index, metadata

def search_index(query_vector, index, metadata, k=5):
    # Ensure the query vector is a NumPy array with dtype float32
    query_vector = np.array(query_vector).astype('float32').reshape(1, -1)

    # Perform the search
    distances, indices = index.search(query_vector, k)

    # Retrieve the metadata for the nearest neighbors
    results = []
    for idx in indices[0]:
        item_id = str(idx)
        if item_id in metadata:
            results.append(metadata[item_id])
        else:
            results.append({'item_id': item_id, 'message': 'Metadata not found'})

    return results


# Function to perform similarity search
def search_faiss_index(query_vector, index, k=5):
    distances, indices = index.search(query_vector, k)
    return distances[0], indices[0]

def fetch_data_from_api(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Assuming the API returns JSON data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return None


@app.route("/")
def home():
     
    return jsonify({"message": "FAISS GPU Service is running!"})

@app.route("/add", methods=["GET", "POST"])
def add_vectors():
    if request.method == "POST":
        return jsonify({"message": "Vectors added successfully!"})
    else:
        return jsonify({"message": "Send a POST request to add vectors."})

@app.route('/search_v2', methods=["GET", "POST"])
def search():
    try:
        # Get the user query from the request
        data = request.get_json()
        user_query = data.get("prompt", "")
        print(f"user_query----------------- :{user_query}")

        if not user_query:
            return jsonify({"error": "Missing query prompt"}), 400

        # Encode the user query to get its embedding
        query_embedding = model.encode(user_query).astype('float32').reshape(1, -1)

        # Number of top results to retrieve
        k = 5

        # Perform the search in the FAISS index
        distances, indices = index.search(query_embedding, k)

        # Retrieve the tmp_image_path for the top k results
        top_k_tmp_image_paths = [
            metadata.get(idx, {}).get("tmp_image_path", None)
            for idx in indices[0]
        ]

        # Filter out None values
        top_k_tmp_image_paths = [path for path in top_k_tmp_image_paths if path]
        print(f"user_query----------------- :{user_query}")

        return jsonify({
            "query": user_query,
            "tmp_image_paths": top_k_tmp_image_paths
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/string-reverse", methods=["POST"])
def string_reverse():
    data = request.get_json()  # Extract text from request body
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400    

    text = data["text"]
    reversed_text = text[::-1]
    print(f'printing reversed text in vector-db-service: [{reversed_text}]')
    return jsonify({"original": text, "reversed": reversed_text})

import mlflow
import numpy as np

import mlflow
import numpy as np

@app.route("/faiss-search", methods=["POST"])
def faiss_search():
    # Set up MLflow tracking
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("RAG_Model_Evaluation")

    with mlflow.start_run():
        # Load FAISS index
        index = faiss.read_index(FAISS_INDEX_PATH)

        with open(FAISS_METADATA_PATH, "r") as f:
            metadata = json.load(f)

        with open(FAISS_INDEX_TO_ITEM_ID_JSON_FILE_PATH, "r") as f:
            faiss_idx_to_item_id_map = json.load(f)

        data = request.get_json()
        user_query = data.get("prompt", "")
        ground_truth = data.get("ground_truth", ["B085D7PY88","B084RRNK4V","B07KGMHN5S","B074H738KL","B07GKZWKHD","B07FP3B2DL","B076573LCD","B07RHV27C6","B074H5BVLD","B074H5BV99"])  # Expected item_ids (if available)

        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(user_query).astype('float32').reshape(1, -1)

        top_k = 3
        distances, indices = index.search(query_embedding, top_k)

        results = []
        relevant_items = 0
        reciprocal_ranks = []
        retrieved_item_ids = []

        for i, faiss_idx in enumerate(indices[0]):
            if faiss_idx == -1:
                continue  

            item_id = faiss_idx_to_item_id_map.get(str(faiss_idx), None)
            if item_id is None:
                continue

            # ✅ Print the retrieved item_id to the console
            print(f"Retrieved item_id at rank {i+1}------------------------: {item_id}")
            retrieved_item_ids.append(item_id)

            if str(item_id) in ground_truth:
                relevant_items += 1
                reciprocal_ranks.append(1 / (i + 1))  

            results.append({
                "rank": i + 1,
                "item_id": item_id,
                "concatenated_desc": metadata.get(item_id, {}).get('concatenated_desc', 'N/A'),
                "image_file_location": metadata.get(item_id, {}).get('image_path', 'N/A'),
                "price": metadata.get(item_id, {}).get('Price', 'N/A'),
                "color_value": metadata.get(item_id, {}).get('color_value', 'N/A')
            })
            
        
        recall_at_k = relevant_items / len(ground_truth) if ground_truth else 0
        precision_at_k = relevant_items / top_k
        mrr = np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0

        # Log Metrics in MLflow (without changing return type)
        mlflow.log_param("Query", user_query)
        mlflow.log_metric("RecallK", recall_at_k)
        mlflow.log_metric("PrecisionK", precision_at_k)
        mlflow.log_metric("MRR", mrr)

        return jsonify(results)  # ✅ Keeping the original return type


    

@app.route("/search", methods=["GET", "POST"])
def search_vectors():
    jsonify({"message": "In search added successfully!"})
   # Your data to send in the request
    data = request.get_json()

    # Set the headers
    headers = {'Content-Type': 'application/json'}

    # Make the POST request with JSON data
    #response = requests.post('http://example.com/api', headers=headers, data=json.dumps(data))
    
   
    # Static query prompt (replace later with dynamic input)
    #user_query = "High-back executive office chair with 360 degree"
    user_query = data.get("prompt", "")
    # Load metadata CSV
    #df = load_metadata()
    # Define the file path
    #print("Current Working Directory:", os.getcwd())
    file_path = "us_listings_images_merged_captioned_v1.csv"

    # Read the CSV into a DataFrame
    df = pd.read_csv(file_path)
    column_names = df.columns
    print(column_names)
    # Convert DataFrame to HTML
    #table_html = df.to_html(classes='data', header="true", index=False)
    #return render_template('table.html', table=table_html)
    # Display first few rows
    #print(df.head())
    if df is None:
        return jsonify({"error": "Metadata CSV not found"}), 400

    df['concatenated_desc'] = df['caption'].astype(str)+" "+ df['bullet_point_value'].astype(str)

     # Initialize the model for embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Generate embeddings and add them as a column
    df['embeddings'] =df['concatenated_desc'].apply(lambda desc: model.encode(desc).astype('float32'))

    # Get the dimension of embeddings (depends on the model used)
    embedding_dim = len(df['embeddings'][0])
     # Parameters for IVF-PQ index
    nlist = 100  # Number of clusters (inverted lists), tune based on dataset size
    m = 8        # Number of sub-quantizers
    nbits = 8    # Bits per sub-quantizer (for 256 centroids per sub-vector)

    
    # Create an IVF-PQ index with Euclidean distance metric
    quantizer = faiss.IndexFlatL2(embedding_dim)  # Underlying index for quantization
    index = faiss.IndexIVFPQ(quantizer, embedding_dim, nlist, m, nbits)


    # Train the index on embeddings (required for IVF-PQ)
    embeddings_array = np.stack(df['embeddings'].values)
    index.train(embeddings_array)
    
    # Dictionary to map FAISS index to item_id
    faiss_index_to_item_id_map = {}

     # Populate FAISS and store metadata by item_id
    metadata = {}
    for i, row in df.iterrows():
        embedding = np.array(row['embeddings'], dtype='float32').reshape(1, -1)
        index.add(embedding)  # Add embedding to FAISS

        # Store metadata using item_id as key
        item_id = row['item_id']
        metadata[item_id] =  {
            "item_id": row['item_id'],
            "item_weight_0_normalized_value_unit": row['item_weight_0_normalized_value_unit'],
            "item_weight_0_normalized_value_value": row['item_weight_0_normalized_value_value'],
            "item_weight_0_unit": row['item_weight_0_unit'],
            "item_weight_0_value": row['item_weight_0_value'],
            "model_number_0_value": row['model_number_0_value'],
            "product_type_0_value": row['product_type_0_value'],
            "main_image_id": row['main_image_id'],
            "color_code_0": row['color_code_0'],
            "country": row['country'],
            "marketplace": row['marketplace'],
            "domain_name": row['domain_name'],
            "item_dimensions_height_normalized_value_unit": row['item_dimensions_height_normalized_value_unit'],
            "item_dimensions_height_normalized_value_value": row['item_dimensions_height_normalized_value_value'],
            "item_dimensions_height_unit": row['item_dimensions_height_unit'],
            "item_dimensions_height_value": row['item_dimensions_height_value'],
            "item_dimensions_length_normalized_value_unit": row['item_dimensions_length_normalized_value_unit'],
            "item_dimensions_length_normalized_value_value": row['item_dimensions_length_normalized_value_value'],
            "item_dimensions_length_unit": row['item_dimensions_length_unit'],
            "item_dimensions_length_value": row['item_dimensions_length_value'],
            "item_dimensions_width_normalized_value_unit": row['item_dimensions_width_normalized_value_unit'],
            "item_dimensions_width_normalized_value_value": row['item_dimensions_width_normalized_value_value'],
            "item_dimensions_width_unit": row['item_dimensions_width_unit'],
            "item_dimensions_width_value": row['item_dimensions_width_value'],
            "model_year_0_value": row['model_year_0_value'],
            "style_value": row['style_value'],
            "item_shape_value": row['item_shape_value'],
            "pattern_value": row['pattern_value'],
            "fabric_type_value": row['fabric_type_value'],
            "item_name_value": row['item_name_value'],
            "material_value": row['material_value'],
            "item_keywords_value": row['item_keywords_value'],
            "finish_type_value": row['finish_type_value'],
            "model_name_value": row['model_name_value'],
            "bullet_point_value": row['bullet_point_value'],
            "color_value": row['color_value'],
            "brand_value": row['brand_value'],
            "Price": row['Price'],
            "caption": row['caption'],
            "concatenated_desc": row['concatenated_desc'],
            "image_path":row['path'],
            "tmp_image_path":row['tmp_image_path']
        }

            # Map FAISS index to item_id
        faiss_index_to_item_id_map[index.ntotal - 1] = item_id  # Current FAISS index
    
           
    jsonify({"status": "success", "message": "Embeddings processed and loaded to FAISS!"}), 200
    
   # Encode the user query to get its embedding
    query_embedding = model.encode(user_query).astype('float32').reshape(1, -1)

    # Number of top results to retrieve
    k = 5

    # Perform the search in the FAISS index
    distances, indices = index.search(query_embedding, k)

    # Retrieve the metadata for the top k results
    #top_k_results = []
    #for idx in indices[0]:
    #    item_id = faiss_index_to_item_id_map[idx]
    #    item_metadata = metadata.get(item_id, {})
    #   top_k_results.append(item_metadata)

    # Return the results as a JSON response
    #return jsonify({"query": user_query, "results": top_k_results}), 200

    # Retrieve the item_ids for the top k results
    top_k_item_ids = [faiss_index_to_item_id_map[idx] for idx in indices[0]]

    # Retrieve the tmp_image_path for the top k results
    top_k_tmp_image_paths = [
        metadata.get(faiss_index_to_item_id_map[idx], {}).get("tmp_image_path", None)
        for idx in indices[0]
        if idx in faiss_index_to_item_id_map  # Ensure index exists in mapping
    ]

    # Filter out None values in case some results have no tmp_image_path
    top_k_tmp_image_paths = [path for path in top_k_tmp_image_paths if path is not None]
    # Return the results as a JSON response
    return jsonify({
        "query": user_query,
        "tmp_image_paths": top_k_tmp_image_paths  # ✅ Returns image paths instead of item IDs
    }), 200


    # Return the results as a JSON response
    #return jsonify({"query": user_query, "top_k_item_ids": top_k_item_ids}), 200



@app.route("/load_data_file_from_s3", methods=["POST"])
def embed_description_and_load_vectors():

    local_directory = LOCAL_DATA_DIR
    #os.path.join(LOCAL_TMP_DOWNLOAD_PATH, S3_DATA_FILE_PATH)
    
    data = request.json
    s3_bucket_name = data['s3_bucket_name']
#    aws_access_key = data['aws_access_key']
#    aws_secret_key = data['aws_secret_key']
    s3_object_key = data['s3_object_key']

    # Extract file name
    file_name = os.path.basename(s3_object_key)
    #file_name = os.path.basename(s3_object_key)


    print(f"File name: {file_name}")
    #print(f'bucket name:{s3_bucket_name}, aws_access_key:{aws_access_key}, aws_secret_key:{aws_secret_key}, fine_name:{file_name}')
    print(f'bucket name:{s3_bucket_name}, fine_name:{file_name}')
    # Log the masked information
    logging.info(
        f'bucket name: {s3_bucket_name}, '
        f'file_name: {file_name}',
        f's3_object_key: {s3_object_key}'
    )

    # Download the CSV from S3

    downloaded = download_file_from_s3(s3_bucket_name, s3_object_key, local_directory)

    if (downloaded):
        delete_file_from_s3(s3_bucket_name, s3_object_key)
    # file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    products_captioned_df = pd.read_csv(os.path.join(local_directory, file_name))
    logging.info('=====================================')
    logging.info(products_captioned_df.info())
    logging.info('====================================')

    products_captioned_df['concatenated_desc'] = products_captioned_df['caption'].astype(str)+" "+ products_captioned_df['bullet_point_value'].astype(str)

    # Initialize the model for embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Generate embeddings and add them as a column
    products_captioned_df['embeddings'] = products_captioned_df['concatenated_desc'].apply(lambda desc: model.encode(desc).astype('float32'))

    # Get the dimension of embeddings (depends on the model used)
    embedding_dim = len(products_captioned_df['embeddings'][0])

    # Parameters for IVF-PQ index
    nlist = 100  # Number of clusters (inverted lists), tune based on dataset size
    m = 8        # Number of sub-quantizers
    nbits = 8    # Bits per sub-quantizer (for 256 centroids per sub-vector)

    
    # Create an IVF-PQ index with Euclidean distance metric
    quantizer = faiss.IndexFlatL2(embedding_dim)  # Underlying index for quantization
    index = faiss.IndexIVFPQ(quantizer, embedding_dim, nlist, m, nbits)


    # Train the index on embeddings (required for IVF-PQ)
    embeddings_array = np.stack(products_captioned_df['embeddings'].values)
    index.train(embeddings_array)
    
    # Dictionary to map FAISS index to item_id
    faiss_index_to_item_id_map = {}

    # Populate FAISS and store metadata by item_id
    metadata = {}
    for i, row in products_captioned_df.iterrows():
        embedding = np.array(row['embeddings'], dtype='float32').reshape(1, -1)
        index.add(embedding)  # Add embedding to FAISS

        # Store metadata using item_id as key
        item_id = row['item_id']
        metadata[item_id] =  {
            "item_id": row['item_id'],
            "item_weight_0_normalized_value_unit": row['item_weight_0_normalized_value_unit'],
            "item_weight_0_normalized_value_value": row['item_weight_0_normalized_value_value'],
            "item_weight_0_unit": row['item_weight_0_unit'],
            "item_weight_0_value": row['item_weight_0_value'],
            "model_number_0_value": row['model_number_0_value'],
            "product_type_0_value": row['product_type_0_value'],
            "main_image_id": row['main_image_id'],
            "color_code_0": row['color_code_0'],
            "country": row['country'],
            "marketplace": row['marketplace'],
            "domain_name": row['domain_name'],
            "item_dimensions_height_normalized_value_unit": row['item_dimensions_height_normalized_value_unit'],
            "item_dimensions_height_normalized_value_value": row['item_dimensions_height_normalized_value_value'],
            "item_dimensions_height_unit": row['item_dimensions_height_unit'],
            "item_dimensions_height_value": row['item_dimensions_height_value'],
            "item_dimensions_length_normalized_value_unit": row['item_dimensions_length_normalized_value_unit'],
            "item_dimensions_length_normalized_value_value": row['item_dimensions_length_normalized_value_value'],
            "item_dimensions_length_unit": row['item_dimensions_length_unit'],
            "item_dimensions_length_value": row['item_dimensions_length_value'],
            "item_dimensions_width_normalized_value_unit": row['item_dimensions_width_normalized_value_unit'],
            "item_dimensions_width_normalized_value_value": row['item_dimensions_width_normalized_value_value'],
            "item_dimensions_width_unit": row['item_dimensions_width_unit'],
            "item_dimensions_width_value": row['item_dimensions_width_value'],
            "model_year_0_value": row['model_year_0_value'],
            "style_value": row['style_value'],
            "item_shape_value": row['item_shape_value'],
            "pattern_value": row['pattern_value'],
            "fabric_type_value": row['fabric_type_value'],
            "item_name_value": row['item_name_value'],
            "material_value": row['material_value'],
            "item_keywords_value": row['item_keywords_value'],
            "finish_type_value": row['finish_type_value'],
            "model_name_value": row['model_name_value'],
            "bullet_point_value": row['bullet_point_value'],
            "color_value": row['color_value'],
            "brand_value": row['brand_value'],
            "Price": row['Price'],
            "caption": row['caption'],
            "concatenated_desc": row['concatenated_desc'],
            "image_path":row['path'],
            "tmp_image_path":row['tmp_image_path']
            
        }

            # Map FAISS index to item_id
        faiss_index_to_item_id_map[index.ntotal - 1] = item_id  # Current FAISS index
    
    # Save FAISS index locally
    local_index_bin_file_path=  FAISS_LOCAL_DB_STORE + '/' + FAISS_INDEX_BIN_FILE
    faiss.write_index(index, local_index_bin_file_path)

    # Save metadata locally
    local_json_metadata_file_path = FAISS_LOCAL_DB_STORE + '/' + FAISS_METADATA_JSON_FILE
    with open(local_json_metadata_file_path, 'w') as f:
        json.dump(metadata, f)
    
    #Save faiss_index_to_item_id_map locally
    local_json_metadata_file_path = FAISS_LOCAL_DB_STORE + '/' + FAISS_INDEX_TO_ITEM_ID_JSON_FILE
    with open(local_json_metadata_file_path, 'w') as f:
        json.dump(faiss_index_to_item_id_map, f)
    
    upload_file_to_s3(s3_bucket_name, FAISS_INDEX_FILE_S3_OBJECT_KEY, local_index_bin_file_path)
    upload_file_to_s3(s3_bucket_name, FAISS_METADATA_JSON_FILE_S3_OBJECT_KEY, local_json_metadata_file_path)
    
    return jsonify({"status": "success", "message": "Embeddings processed and loaded to FAISS!"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)