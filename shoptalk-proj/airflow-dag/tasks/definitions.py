
import os
import tarfile
import requests
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import shutil
import gzip
import glob
import json
from utils.json_utils import flatten_json
from utils.s3_utils import upload_file_to_s3, download_file_from_s3
from utils.generic_utils import copy_file, generate_captions_batch, validate_and_get_image_path
import re
import numpy as np
#import mlflow
#from sentence_transformers import SentenceTransformer

##### Captioning related
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import os
from tqdm import tqdm
from PIL import Image
##################
import torch


from datetime import datetime, timedelta
from config import LISTINGS_DOWNLOAD_PATH_URL, LOCAL_RAW_DATA_DIR, ALL_LISTINGS_DATA_CSV, US_ONLY_LISTINGS_CSV, US_ONLY_LISTINGS_FILTERED_V1_CSV, US_ONLY_LISTINGS_FILTERED_V2_CSV,  US_PRODUCT_IMAGE_MERGE_CSV, AWS_S3_BUCKET, LISTINGS_CSV_FILE_LOCATION, IMAGES_DOWNLOAD_PATH_URL,LOCAL_RAW_IMGS_DIR, IMAGES_CSV_FILE_LOCATION, IMAGES_CSV_FILE, TMP_LISTINGS_SOURCE, TAR_FILE_NAME, US_ONLY_LISTINGS_IMAGES_MERGED_CSV, SMALL_IMAGE_HOME_PATH, US_ONLY_LISTINGS_IMAGES_MERGED_CLEANED_CSV, US_ONLY_LISTINGS_IMAGES_MERGED_CAPTIONED_CSV, CAPTIONED_CSV_FILE_S3_LOCATION

#from s3_download import download_file_from_s3
def download_tar_file(**kwargs):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID
        
    """Download the tar file from a URL."""
    local_tar_path = os.path.join(LOCAL_RAW_DATA_DIR,"abo-listings.tar")
    
    
    if os.path.exists(local_tar_path):    
        print(f"File already downloaded and exits: {local_tar_path}.")
        return
    
    response = requests.get(LISTINGS_DOWNLOAD_PATH_URL, stream=True)
    print(f'Check URL: {LISTINGS_DOWNLOAD_PATH_URL}')
    print(response)
    print('Check-end')
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    # Save the file to disk in chunks
    with open(local_tar_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    files = os.listdir(LOCAL_RAW_DATA_DIR)
    print(f'Files at {LOCAL_RAW_DATA_DIR} : {files}')            
    print(f"Downloaded tar file to {LOCAL_RAW_DATA_DIR}")




def copy_listings_tar_file(source_path, destination_path, tar_file_name):
    
###    "source_path": TMP_LISTINGS_SOURCE,==> /opt/airflow/downloads
###    "destination_path": LOCAL_RAW_DATA_DIR, ==> /opt/airflow/data/raw
###    "tar_file_name" : TAR_FILE_NAME  ==> abo-listings.tar
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID
    
    source = os.path.join(source_path, tar_file_name)
    #######source ===> /opt/airflow/downloads/abo-listings.tar
    # Ensure the source file exists
    if not os.path.isfile(source):
        print(f"Source file does not exist: {source_path}")
        return
    
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    try:
        # Copy the .tar file
        shutil.copy(source, destination_path)
        print(f"File copied successfully to {destination_path}")
    except Exception as e:
        print(f"Error while copying file: {e}")

def extract_tar_file(extract_dir_path, tar_file, local_extracted_json_dir, extracted_file_pattern, decompressed_json_file_pattern):        
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID    
    
    local_tar_path = os.path.join(extract_dir_path, tar_file)
    compressed_json_dir = os.path.join(extract_dir_path, local_extracted_json_dir)
    
    # Check if directory exists [/home/sagar/Work/IK/CapStone-ShopTalk/PROJECT/ShopTalk/data/raw/listings/metadata]
    if os.path.exists(compressed_json_dir) and os.path.isdir(compressed_json_dir):
        print(f"The directory '{compressed_json_dir}' exists.")
    
    # extracted_file_pattern_path[/home/sagar/Work/IK/CapStone-ShopTalk/PROJECT/ShopTalk/data/raw/listings/metadata/listings_?.json.gz]
    extracted_file_pattern_path = os.path.join(compressed_json_dir, extracted_file_pattern)
    file_pattern = os.path.expanduser(extracted_file_pattern_path)
    print(f'file_pattern: {file_pattern}')
    print(f'extracted_file_pattern: {extracted_file_pattern}')
    matching_files = glob.glob(extracted_file_pattern_path)
    print(f'matching_files: {matching_files}')
    if matching_files:
        print(f"Files matching the pattern '{file_pattern}' exist:")
        for file in matching_files:
            print(f" - {file}")
        print(f"Tar file {tar_file} already extracted. Moving to next Task")
        
    
    decompressed_file_pattern_path = os.path.join(compressed_json_dir, decompressed_json_file_pattern)
    print(f' decompressed_file_pattern_path :{decompressed_file_pattern_path}')
    decompressed_file_pattern = os.path.expanduser(decompressed_file_pattern_path)
    print(f' decompressed_file_pattern :{decompressed_file_pattern}')
    matching_files = glob.glob(decompressed_file_pattern_path)
    print(f'matching_files: {matching_files}')
    if matching_files:
        print(f"Files matching the pattern '{file_pattern}' exist:")
        for file in matching_files:
            print(f" - {file}")
        print(f"Tar file {tar_file} already extracted. Moving to next Task")
        return
    
    print(f'extract-1 :{compressed_json_dir}')
    if not os.path.exists(local_tar_path):
        raise FileNotFoundError(f"Tar file not found: {local_tar_path}")
    # Ensure the extraction directory exists
    print('extract-2')
    try:
        # Open the tar file in read mode
        with tarfile.open(local_tar_path, "r:*") as tar:
            tar.extractall(extract_dir_path)
        print('extract-3')
        print(f"Successfully extracted tar file to: {extract_dir_path}")        
    except tarfile.TarError as e:
        print(f"Error extracting tar file: {e}")
        raise
    print('extract-4')
    
    
    files = os.listdir(compressed_json_dir)
    print(f'files {files}')
    for file_i in files:            
        print(file_i)
        compressed_json_path = os.path.join(compressed_json_dir, file_i)
        print(f'compressed_json_path :{compressed_json_path}')
        base_file = os.path.splitext(compressed_json_path)[0]
        with gzip.open(compressed_json_path, 'rb') as gz_file:
            type(compressed_json_path)
            print(compressed_json_path)
            print(compressed_json_path.split('.'))
            # Remove the .gz extension
            
            print(f'Base File : {base_file}')
            with open(base_file, 'wb') as decompressed_file:
                shutil.copyfileobj(gz_file, decompressed_file)
                print(f'Extracted file {decompressed_file}')
        
    
    files = os.listdir(compressed_json_dir)
    print(f'Files at {compressed_json_dir} : {files}')       

def flatten_each_json_and_save_as_csv(local_extracted_json_dir):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID
        
    print("ENTERED flatten_json_and_load_to_dataframe ***************")
    directory_path= os.path.join(LOCAL_RAW_DATA_DIR, local_extracted_json_dir)
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]    
    print(f"JSON FILES LIST :{json_files}")
    
    for listing_file in json_files:
        
        print(f'Processing : {listing_file}')
        listing_file_path = os.path.join(directory_path, listing_file)
        print(listing_file_path)
        flattened_data = []
        with open(listing_file_path, 'r') as f:
            for line in f:
                json_obj = json.loads(line.strip())  # Load JSON from each line
                flattened_data.append(flatten_json(json_obj))
        
        flattened_json_as_df = pd.json_normalize(flattened_data)
        base_file_name = listing_file.split('.')[0]
        csv_file = directory_path +'/'+ base_file_name + '.csv'
        flattened_json_as_df.to_csv(csv_file)      
        print(f'saved : {listing_file} as {csv_file}')  


    

def flatten_all_json_and_save_as_csv(local_extracted_json_dir, **kwargs):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID    
    

    
    print("ENTERED flatten_json_and_load_to_dataframe ***************")
    directory_path= os.path.join(LOCAL_RAW_DATA_DIR, local_extracted_json_dir)
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    #raw_data_df=pd.DataFrame()
    print(f"JSON FILES LIST :{json_files}")

    us_listings_raw_df = pd.DataFrame()
    for listing_file in json_files:
        print(f'Processing : {listing_file}')
        listing_file_path = os.path.join(directory_path, listing_file)
        print(listing_file_path)
        flattened_data = []
        with open(listing_file_path, 'r') as f:
            for line in f:
                json_obj = json.loads(line.strip())  # Load JSON from each line
                flattened_data.append(flatten_json(json_obj))

        flattened_json_as_df = pd.json_normalize(flattened_data)
        base_file_name = listing_file.split('.')[0]
        csv_file = directory_path +'/'+ base_file_name + '.csv'
        flattened_json_as_df.to_csv(csv_file)
        
        us_listing_df = flattened_json_as_df[flattened_json_as_df['country'] == 'US']
        us_listings_raw_df  = pd.concat([ us_listings_raw_df ,  us_listing_df ], ignore_index=True)
        print(f'saved : {listing_file} as {csv_file}')
        

    print(us_listings_raw_df.info())
    all_US_listings_csv_file = directory_path +'/'+ US_ONLY_LISTINGS_CSV
    us_listings_raw_df.to_csv(all_US_listings_csv_file)
    print(f"US_listings raw data is saved to :{all_US_listings_csv_file}")
    
    # Return the path to the CSV file for XCom
    return all_US_listings_csv_file

def load_us_data_and_perform_eda(local_tmp_dir, **kwargs):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID
    
    
    
    directory_path= os.path.join(LOCAL_RAW_DATA_DIR, local_tmp_dir)
    
    # Retrieve the file path from XCom
    ti = kwargs['ti']
    all_US_listings_csv_file = ti.xcom_pull(task_ids="flatten_all_json_and_save_US_data_as_csv")
    US_DF = pd.read_csv(all_US_listings_csv_file)
    
    language_tag_columns = [col for col in US_DF.columns if 'language_tag' in col]
    value_columns =  [col.replace('language_tag', 'value') for col in language_tag_columns]

    language_df=US_DF[language_tag_columns ].copy()
    value_df=US_DF[value_columns].copy()
    
    
    distinct_columns_set = {re.sub(r'_\d+_language_tag', '', col) for col in language_tag_columns}
    
    lang_val_merge_df = pd.DataFrame()
    for a_col in distinct_columns_set:
        the_column_list = []
        prefix = a_col + '_'
        print(prefix)
        the_column_list = [col for col in US_DF.columns if prefix in col]
        the_column_list = [col for col in the_column_list if 'standardized' not in col]
        the_column_list = [col for col in the_column_list if 'alternate_representations' not in col]

        num_brand_keypairs = len(the_column_list)//2
        print(the_column_list)
        a_col_value= prefix + 'value'
        lang_val_merge_df[a_col_value] = US_DF.apply(
            lambda row: ' '.join(
                str(row[f'{prefix}{i}_value'])
                for i in range(num_brand_keypairs)
                if row[f'{prefix}{i}_language_tag'] == 'en_US'
            ).strip(),
            axis=1
        )
        
        
    US_DF.drop(columns=language_tag_columns, inplace=True)
    US_DF.drop(columns=value_columns, inplace=True)
    
    df_new = US_DF.drop([col for col in US_DF.columns if 'standardized' in col], axis=1)
    df_new2 = df_new.drop([col for col in df_new.columns if 'alternate_representations' in col], axis=1)
    
    US_DF_filtered = pd.concat([df_new2, lang_val_merge_df], axis=1)
    
    # TODO:he following line applies for the entire of the dataset
    #drop_column_list1=['product_description_value','other_image_id_0', 'other_image_id_1', 'other_image_id_2', 'other_image_id_3', 'other_image_id_4', 'other_image_id_5', 'other_image_id_6', 'other_image_id_7', 'other_image_id_8', 'other_image_id_9', 'other_image_id_10', 'other_image_id_11', 'other_image_id_12', 'other_image_id_13', 'other_image_id_14', 'other_image_id_15', 'other_image_id_16', 'other_image_id_17', 'other_image_id_18', 'other_image_id_19', 'spin_id', '3dmodel_id', 'node_0_node_id', 'node_0_node_name', 'node_1_node_id', 'node_1_node_name', 'node_2_node_id', 'node_2_node_name', 'node_3_node_id', 'node_3_node_name', 'node_4_node_id', 'node_4_node_name', 'node_5_node_id', 'node_5_node_name', 'node_6_node_id', 'node_6_node_name', 'node_7_node_id', 'node_7_node_name', 'node_8_node_id', 'node_8_node_name', 'node_9_node_id', 'node_9_node_name', 'node_10_node_id', 'node_10_node_name']
    
    #The following like applies only to us_listings_9 and us_listings_a. Comment this out later.
    drop_column_list1=['product_description_value','other_image_id_0', 'other_image_id_1', 'other_image_id_2', 'other_image_id_3', 'other_image_id_4', 'other_image_id_5', 'other_image_id_6', 'other_image_id_7', 'other_image_id_8', 'other_image_id_9', 'other_image_id_10', 'other_image_id_11', 'other_image_id_12', 'other_image_id_13', 'other_image_id_14','spin_id', '3dmodel_id', 'node_0_node_id', 'node_0_node_name', 'node_1_node_id', 'node_1_node_name', 'node_2_node_id', 'node_2_node_name', 'node_3_node_id', 'node_3_node_name', 'node_4_node_id', 'node_4_node_name', 'node_5_node_id', 'node_5_node_name', 'node_6_node_id', 'node_6_node_name', 'node_7_node_id', 'node_7_node_name', 'node_8_node_id', 'node_8_node_name']
    US_DF_filtered3= US_DF_filtered.drop(columns=drop_column_list1)
    
    
    US_DF_filtered4 = US_DF_filtered3.dropna(subset=['main_image_id'])
    ## Add random "PRICE" Colume to the data set
    US_DF_filtered4['Price'] = np.random.uniform(20, 100, size=len(US_DF_filtered4)).round(2)
    
    all_US_listings_filtered_v1_csv_file = directory_path +'/'+ US_ONLY_LISTINGS_FILTERED_V1_CSV
    US_DF_filtered4.to_csv(all_US_listings_filtered_v1_csv_file)
    print(f"US_listdrings filtered data is saved to :{all_US_listings_filtered_v1_csv_file}") 
    
    kwargs['ti'].xcom_push(key='all_US_listings_filtered_v1_csv_file', value=all_US_listings_filtered_v1_csv_file)
    
    #return all_US_listings_filtered_v1_csv_file


    

def perform_eda_on_us_listings_data(local_dir, **kwargs):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID    
    
    directory_path = os.path.join(LOCAL_RAW_DATA_DIR,  local_dir)
    all_US_listings_filtered_csv_file = directory_path +'/'+ US_ONLY_LISTINGS_CSV
    US_DF = pd.read_csv(all_US_listings_filtered_csv_file)
    
    ## Replacing 
    language_tag_columns = [col for col in US_DF.columns if 'language_tag' in col]
    value_columns =  [col.replace('language_tag', 'value') for col in language_tag_columns]

    language_df=US_DF[language_tag_columns ].copy()
    value_df=US_DF[value_columns].copy()
    distinct_columns_set = {re.sub(r'_\d+_language_tag', '', col) for col in language_tag_columns}
    
    lang_val_merge_df = pd.DataFrame()

    for a_col in distinct_columns_set:
        the_column_list = []
        prefix = a_col + '_'
        print(prefix)
        the_column_list = [col for col in US_DF.columns if prefix in col]
        the_column_list = [col for col in the_column_list if 'standardized' not in col]
        the_column_list = [col for col in the_column_list if 'alternate_representations' not in col]

        num_brand_keypairs = len(the_column_list)//2
        print(the_column_list)
        a_col_value= prefix + 'value'
        lang_val_merge_df[a_col_value] = US_DF.apply(
            lambda row: ' '.join(
                str(row[f'{prefix}{i}_value'])
                for i in range(num_brand_keypairs)
                if row[f'{prefix}{i}_language_tag'] == 'en_US'
            ).strip(),
            axis=1
        )
    
    US_DF.drop(columns=language_tag_columns, inplace=True)
    US_DF.drop(columns=value_columns, inplace=True)
    
    df_new = US_DF.drop([col for col in US_DF.columns if 'standardized' in col], axis=1)
    df_new2 = df_new.drop([col for col in df_new.columns if 'alternate_representations' in col], axis=1)
    
    US_DF_filtered = pd.concat([df_new2, lang_val_merge_df], axis=1)
    
    #The following line applies to all us_listings data. U comment later.
    #drop_column_list1=['spin_id', '3dmodel_id', 'node_0_node_id', 'node_0_node_name', 'node_1_node_id', 'node_1_node_name', 'node_2_node_id', 'node_2_node_name', 'node_3_node_id', 'node_3_node_name', 'node_4_node_id', 'node_4_node_name', 'node_5_node_id', 'node_5_node_name', 'node_6_node_id', 'node_6_node_name', 'node_7_node_id', 'node_7_node_name', 'node_8_node_id', 'node_8_node_name', 'node_9_node_id', 'node_9_node_name', 'node_10_node_id', 'node_10_node_name']
    
    #The following line applies to us_listings_9 and us_listings_a. So delete later
    drop_column_list1=['spin_id', '3dmodel_id', 'node_0_node_id', 'node_0_node_name', 'node_1_node_id', 'node_1_node_name', 'node_2_node_id', 'node_2_node_name', 'node_3_node_id', 'node_3_node_name', 'node_4_node_id', 'node_4_node_name', 'node_5_node_id', 'node_5_node_name', 'node_6_node_id', 'node_6_node_name', 'node_7_node_id', 'node_7_node_name', 'node_8_node_id', 'node_8_node_name']
    US_DF_filtered3= US_DF_filtered.drop(columns=drop_column_list1)
    US_DF_filtered4 = US_DF_filtered3.dropna(subset=['main_image_id'])
    US_DF_filtered4['Price'] = np.random.uniform(20, 100, size=len(US_DF_filtered4)).round(2)    
    
    
    all_US_listings_filtered_v2_csv_file = directory_path +'/'+ US_ONLY_LISTINGS_FILTERED_V2_CSV
    US_DF_filtered4.to_csv(all_US_listings_filtered_v2_csv_file, index=False)
    print(f"US_listings filtered data is saved to :{all_US_listings_filtered_v2_csv_file}") 
    
    kwargs['ti'].xcom_push(key='all_US_listings_filtered_v2_csv_file', value=all_US_listings_filtered_v2_csv_file)
    return all_US_listings_filtered_v2_csv_file
    



def flatten_to_csv_images(**kwargs):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID
        
    """Decompress and flatten the image metadata to a CSV file."""
    metadata_gz_path = os.path.join(LOCAL_RAW_IMGS_DIR, "images/metadata/images.csv.gz")
    output_csv_path = os.path.join(LOCAL_RAW_IMGS_DIR, "images_metadata.csv")

    # Check if the compressed metadata file exists
    if not os.path.exists(metadata_gz_path):
        raise FileNotFoundError(f"Metadata file not found: {metadata_gz_path}")

    print(f"Decompressing and processing metadata file: {metadata_gz_path}")
    decompressed_file_path = metadata_gz_path.rstrip(".gz")

    # Decompress the .gz file
    with gzip.open(metadata_gz_path, "rb") as f_in:
        with open(decompressed_file_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    # Read the decompressed CSV file
    metadata_df = pd.read_csv(decompressed_file_path)
    print(f"Metadata columns: {metadata_df.columns}")
    print(f"Number of records in metadata: {len(metadata_df)}")

    # Save the decompressed metadata to a flat CSV file
    metadata_df.to_csv(output_csv_path, index=False)
    print(f"Flattened metadata saved to: {output_csv_path}")
    kwargs['ti'].xcom_push(key='image_file_csv', value=output_csv_path)




def download_tar_file_images(**kwargs):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID
    
    """Download the image tar file from the specified URL."""
    # Define the local path to save the tar file
    local_tar_path = os.path.join(LOCAL_RAW_IMGS_DIR, "abo-images-small.tar")

    # Check if the file already exists to avoid re-downloading
    if os.path.exists(local_tar_path):
        print(f"File already downloaded and exists: {local_tar_path}.")
        return

    # Make the local directory if it doesn't exist
    os.makedirs(LOCAL_RAW_IMGS_DIR, exist_ok=True)

    # Download the tar file from the specified URL
    response = requests.get(IMAGES_DOWNLOAD_PATH_URL, stream=True)
    print(f"Downloading from URL: {IMAGES_DOWNLOAD_PATH_URL}")
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Save the file to disk in chunks
    with open(local_tar_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # List files in the directory for confirmation
    files = os.listdir(LOCAL_RAW_IMGS_DIR)
    print(f"Files at {LOCAL_RAW_IMGS_DIR}: {files}")
    print(f"Downloaded tar file to {local_tar_path}")




def extract_tar_file_images(**kwargs):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID
    
    """Extract the image tar file and process metadata and images."""
    ########### LOCAL_RAW_IMGS_DIR="/opt/airflow/data/rawimages"    
    tar_file_path = os.path.join(LOCAL_RAW_IMGS_DIR, "abo-images-small.tar")
    #####tar_file_path==> /opt/airflow/data/rawimages/abo-images-small.tar
    extract_dir = LOCAL_RAW_IMGS_DIR
    ######extract_dir==/opt/airflow/data/rawimages

    # Check if the tar file exists
    if not os.path.exists(tar_file_path):
        raise FileNotFoundError(f"Tar file not found: {tar_file_path}")

    # Check if already extracted
    ####checking for /opt/airflow/data/rawimages/images
    if os.path.exists(os.path.join(extract_dir, "images")):
        print(f"Tar file already extracted to: {extract_dir}. Skipping extraction.")
        return

    print(f"Extracting tar file: {tar_file_path}")
    try:
        # Open the tar file and extract its contents
        with tarfile.open(tar_file_path, "r:*") as tar:
            tar.extractall(extract_dir)
        print(f"Successfully extracted tar file to: {extract_dir}")
    except tarfile.TarError as e:
        print(f"Error extracting tar file: {e}")
        raise    

def up_load_us_listings_to_s3():
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    print(f'aws_access_key: {aws_access_key_id} - aws_secret_access_key: {aws_secret_access_key}')
    print(f' AWS_S3_BUCKET: {AWS_S3_BUCKET}')    
    
    local_file_path2 = LISTINGS_CSV_FILE_LOCATION + 'us_listings.csv'
    print(f'local_file_path2: {os.path.exists(local_file_path2)}')
    upload_file_to_s3( AWS_S3_BUCKET, "listings/us_listings.csv", local_file_path2 )

    

def merge_listings_images(local_dir, **kwargs):
    # Read from local and merge
    
    ti = kwargs['ti']
    
    us_listings_filtered_file_csv = ti.xcom_pull(task_ids='perform_eda_on_us_listings_data', key='all_US_listings_filtered_v2_csv_file')  # Pulling from Task B
    image_file_csv = ti.xcom_pull(task_ids='flatten_to_csv_images', key='image_file_csv')  # Pulling from Task A
    
    
    print(f"Collected US_LISTINGS_CSV: {us_listings_filtered_file_csv} and IMAGES_CSV: {image_file_csv}")
    print(f'MERGED listings and images dataframes')
    
    us_listings_csv_df = pd.read_csv(us_listings_filtered_file_csv)  
    images_csv_df = pd.read_csv(image_file_csv)      
    
    merged_df = pd.merge(us_listings_csv_df, 
                         images_csv_df, 
                         left_on='main_image_id', 
                         right_on='image_id', 
                         how='left')
    print('Listings and Image data merged into one dataframe')
    print(merged_df.info())
    ## Save to a file
    directory_path = os.path.join(LOCAL_RAW_DATA_DIR,  local_dir)
    all_US_listings_images_merged_v1_csv_file = directory_path +'/'+ US_ONLY_LISTINGS_IMAGES_MERGED_CSV
    merged_df.to_csv(all_US_listings_images_merged_v1_csv_file, index=False)
    print(f"CSV saved at: {all_US_listings_images_merged_v1_csv_file}")
    
    kwargs['ti'].xcom_push(key='all_US_listings_images_merged_v1_csv_file', value=all_US_listings_images_merged_v1_csv_file)
    return all_US_listings_images_merged_v1_csv_file
    



    



def drop_if_image_file_missing(local_dir, **kwargs):
    ti = kwargs['ti']
    all_US_listings_images_merged_v1_csv_file = ti.xcom_pull(task_ids='merge_listings_image_df_task', key='all_US_listings_images_merged_v1_csv_file')  # Pulling from Task B
    merged_df = pd.read_csv(all_US_listings_images_merged_v1_csv_file)
    print(f'==================')
    print(merged_df.info())
    print(f'==================')

    # Use a lambda function to pass both parameters
    merged_df['tmp_image_path'] = merged_df['path'].apply(lambda postfix_path: validate_and_get_image_path(SMALL_IMAGE_HOME_PATH, postfix_path))

    # Drop rows where tmp_image_path is None (invalid images)
    filtered_df = merged_df.dropna(subset=['tmp_image_path'])

    print(f'==================')
    print(filtered_df.info())
    print(f'==================')   

    
    directory_path = os.path.join(LOCAL_RAW_DATA_DIR,  local_dir)
    all_US_listings_images_merged_cleaned_v1_csv_file = directory_path +'/'+ US_ONLY_LISTINGS_IMAGES_MERGED_CLEANED_CSV
    filtered_df.to_csv(all_US_listings_images_merged_cleaned_v1_csv_file, index=False)
    kwargs['ti'].xcom_push(key='all_US_listings_images_merged_cleaned_v1_csv_file', value=all_US_listings_images_merged_cleaned_v1_csv_file)
    print(f'==================')
    print(filtered_df.info())
    print(f'==================')
    return all_US_listings_images_merged_cleaned_v1_csv_file



def generate_image_captions(local_dir, **kwargs):
    if torch.cuda.is_available():
        print("CUDA is available! Using GPU for inference.")
        device = torch.device("cuda")
    else:
        print("CUDA is not available. Using CPU for inference.")
        device = torch.device("cpu")
    
    print(f' DEVICE:{device}')
    ti = kwargs['ti']
    
    all_US_listings_images_merged_cleaned_v1_csv_file = ti.xcom_pull(task_ids='merged_data_clean_up_task', key='all_US_listings_images_merged_cleaned_v1_csv_file')  # Pulling from Task A
    merged_df = pd.read_csv(all_US_listings_images_merged_cleaned_v1_csv_file)
    print(f'======================')
    print(merged_df.info())
    print(f'======================')
    # Pre-load the model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    print(f'Processor :{processor}')
    print(f'Model :{model}')
     # Batch size
    #Was 246 had to change to 128 becuase of OOM error. Try changing to 256 again.
    batch_size = 128  # Adjust according to your system's memory capacity
   # print(f'SAMPLE PATH: {os.path.join(SMALL_IMAGE_HOME_PATH, merged_df.loc[5, "image_path"])}')
    
    # Move to Cuda device
    model.to(device)

    # Process images in batches
    print(f'len(merged_df): {len(merged_df)}')
    for i in tqdm(range(0, len(merged_df), batch_size)):  
        batch_paths = [
            os.path.join(SMALL_IMAGE_HOME_PATH, merged_df.loc[idx, "path"])
            for idx in range(i, min(i + batch_size, len(merged_df)))
        ]      
        batch_paths = [path for path in batch_paths if os.path.exists(path)]

        # Generate captions for the batch
        print(f' Paths list :[ {batch_paths}]')
        try:            
            images = [Image.open(path).convert("RGB") for path in batch_paths]
            captions = generate_captions_batch(batch_paths, device, processor, model)
            print(f'Generated Captions List [:{captions}]')
        #     # Assign captions to the dataframe
            merged_df.loc[i:i + len(captions) - 1, 'caption'] = captions
        except (Image.UnidentifiedImageError, FileNotFoundError) as e:
            print(f"Error processing batch starting at index {i}: {e}")
    
    directory_path = os.path.join(LOCAL_RAW_DATA_DIR,  local_dir)
    all_US_listings_images_captioned_v1_csv_file = directory_path +'/'+ US_ONLY_LISTINGS_IMAGES_MERGED_CAPTIONED_CSV
    merged_df.to_csv(all_US_listings_images_captioned_v1_csv_file, index=False)
    print(f'======================')
    print(merged_df.info())
    print(f'======================')
    kwargs['ti'].xcom_push(key='all_US_listings_images_captioned_v1_csv_file', value=all_US_listings_images_captioned_v1_csv_file)
    return all_US_listings_images_captioned_v1_csv_file

def upload_captions_to_s3(bucket_name, local_dir, **kwargs):
     
     ti = kwargs['ti']

     all_US_listings_images_captioned_v1_csv_file = ti.xcom_pull(task_ids='generate_image_captions_task', key='all_US_listings_images_captioned_v1_csv_file')  # Pulling from Task A
     
     directory_path = os.path.join(LOCAL_RAW_DATA_DIR, local_dir)
    # file_name = "all_US_listings_images_captioned_v1.csv"  # Ensure the correct file name
     #file_path = os.path.join(CAPTIONED_CSV_FILE_S3_LOCATION, all_US_listings_images_captioned_v1_csv_file)
     s3_object_key = f"{CAPTIONED_CSV_FILE_S3_LOCATION}{US_ONLY_LISTINGS_IMAGES_MERGED_CAPTIONED_CSV}"
     print(f"path:{all_US_listings_images_captioned_v1_csv_file}")
     upload_file_to_s3(bucket_name, s3_object_key, all_US_listings_images_captioned_v1_csv_file)

    
    