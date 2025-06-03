BUCKET_NAME="shoptalk-g1-bucket"
S3_DATA_FILE_PATH="products-listings/US_DF_with_price_and_caption.csv"


LOCAL_DATA_DIR="/app/data/"
#### CHROMA
LOCAL_CHROMA_DB_STORE="/app/vector_database/chroma_db"
#### FAISS 
#FAISS_LOCAL_DB_STORE="shop-talk/shoptalk-proj/vector_database/faiss_db" 
FAISS_LOCAL_DB_STORE="/app/vector_database/faiss_db"
FAISS_METADATA_JSON_FILE="faiss_metadata.json"
FAISS_INDEX_BIN_FILE="faiss_index.bin"
FAISS_INDEX_TO_ITEM_ID_JSON_FILE="faiss_index_to_item_id.json"



# FAISS_LOCAL_DB_STORE, FAISS_INDEX_BIN_FILE
### S3 #######
FAISS_INDEX_FILE_S3_OBJECT_KEY="vector-datastore/faiss/faiss_index.bin"
FAISS_METADATA_JSON_FILE_S3_OBJECT_KEY="vector-datastore/faiss/faiss_metadata.json"


FAISS_INDEX_PATH="/app/vector_database/faiss_db/faiss_index.bin"
FAISS_METADATA_PATH="/app/vector_database/faiss_db/faiss_metadata.json"
FAISS_INDEX_TO_ITEM_ID_JSON_FILE_PATH="/app/vector_database/faiss_db/faiss_index_to_item_id.json"
