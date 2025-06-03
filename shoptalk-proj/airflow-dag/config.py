TMP_LISTINGS_SOURCE="/opt/airflow/downloads"
TAR_FILE_NAME='abo-listings.tar'

TMP_IMAGE_DOWNLOAD_LOCATION="/opt/airflow/downloads/abo-images-small.tar"
TMP_LISTINGS_DOWNLOAD_LOCATION="/opt/airflow/downloads/abo-listings.tar"
#abo-images-small.tar"
IMAGES_OBJECT_S3_KEY_ID="image-data-subset/abo-images-small.tar"
LISTINGS_OBJECT_S3_KEY_ID="listings-data-subset/abo-listings.tar"




LISTINGS_DOWNLOAD_PATH_URL="https://amazon-berkeley-objects.s3.amazonaws.com/archives/abo-listings.tar"
LOCAL_RAW_DATA_DIR="/opt/airflow/data/raw"
ALL_LISTINGS_DATA_CSV="all_listings.csv"
US_ONLY_LISTINGS_CSV="us_listings.csv"
US_ONLY_LISTINGS_FILTERED_V1_CSV="us_listings_filtered_v1.csv"
US_ONLY_LISTINGS_FILTERED_V2_CSV="us_listings_filtered_v2.csv"
US_ONLY_LISTINGS_IMAGES_MERGED_CSV="us_listings_images_merged_v1.csv"
US_ONLY_LISTINGS_IMAGES_MERGED_CLEANED_CSV="us_listings_images_merged_cleaned_v1.csv"
US_ONLY_LISTINGS_IMAGES_MERGED_CAPTIONED_CSV="us_listings_images_merged_captioned_v1.csv"
US_PRODUCT_IMAGE_MERGE_CSV="us_product_image_merged.csv"
LISTINGS_CSV_FILE_LOCATION="/opt/airflow/data/raw/listings/metadata/"
AWS_S3_BUCKET="shoptalk-g1-bucket"
CAPTIONED_CSV_FILE_S3_LOCATION="captioned_data/"
S3_CAPTIONED_OBJECT_KEY="captioned_data/us_listings_images_merged_captioned_v1.csv"
FAISS_API_ENDPOINT="http://vector-db-service:8000/load_data_file_from_s3"
FAISS_API_SEARCH_ENDPOINT="http://vector-db-service:8000/search"


IMAGES_DOWNLOAD_PATH_URL="https://amazon-berkeley-objects.s3.amazonaws.com/archives/abo-images-small.tar"
LOCAL_RAW_IMGS_DIR="/opt/airflow/data/rawimages"
IMAGES_CSV_FILE_LOCATION="/opt/airflow/data/rawimages/images/metadata"
IMAGES_CSV_FILE="images.csv"


##########
SMALL_IMAGE_HOME_PATH="/opt/airflow/data/rawimages/images/small/"


