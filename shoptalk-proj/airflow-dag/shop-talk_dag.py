import os
import tarfile
import requests
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.s3_key_sensor import S3KeySensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from datetime import datetime
import shutil
import gzip
import glob
import json
from utils.json_utils import flatten_json
from utils.s3_utils import upload_file_to_s3, download_file_from_s3
from utils.generic_utils import copy_file

import re
import numpy as np
#import mlflow
#from sentence_transformers import SentenceTransformer

from datetime import datetime, timedelta


from config import LISTINGS_DOWNLOAD_PATH_URL, LOCAL_RAW_DATA_DIR, ALL_LISTINGS_DATA_CSV, US_ONLY_LISTINGS_CSV, US_PRODUCT_IMAGE_MERGE_CSV, AWS_S3_BUCKET, LISTINGS_CSV_FILE_LOCATION, IMAGES_DOWNLOAD_PATH_URL,LOCAL_RAW_IMGS_DIR, IMAGES_CSV_FILE_LOCATION, IMAGES_CSV_FILE, TMP_LISTINGS_SOURCE, TAR_FILE_NAME, TMP_IMAGE_DOWNLOAD_LOCATION, IMAGES_OBJECT_S3_KEY_ID, S3_CAPTIONED_OBJECT_KEY, FAISS_API_ENDPOINT, FAISS_API_SEARCH_ENDPOINT, TMP_LISTINGS_DOWNLOAD_LOCATION, LISTINGS_OBJECT_S3_KEY_ID
from tasks.definitions import download_tar_file, extract_tar_file, flatten_each_json_and_save_as_csv, flatten_all_json_and_save_as_csv, perform_eda_on_us_listings_data, flatten_to_csv_images, download_tar_file_images, extract_tar_file_images, up_load_us_listings_to_s3, merge_listings_images, copy_listings_tar_file, load_us_data_and_perform_eda, merge_listings_images, generate_image_captions, drop_if_image_file_missing, upload_captions_to_s3


# DAG definition
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="shoptalk_ingestion_pipeline",
    default_args=default_args,
    description="Pipeline to download, extract, and process product listings",
    start_date=datetime(2024, 1, 1),
    #schedule_interval="@daily",
    #schedule_interval="*/10 * * * *",  # Every 10 minutes
    schedule_interval=None,
    max_active_runs=3,
    catchup=False,
) as dag:

## TEmporarily disable download task instead have copy task

    # download_task = PythonOperator(
    #     task_id="download_tar_file",
    #     python_callable=download_tar_file,
    #     dag=dag
    # )



    copy_listings_from_s3 = PythonOperator(
        task_id="copy_listings_to_local_folder",
        python_callable=download_file_from_s3,
        task_concurrency=2,
        op_kwargs={
                    "bucket_name": AWS_S3_BUCKET,
                    "file_name" : LISTINGS_OBJECT_S3_KEY_ID,
                    "local_file_path": TMP_LISTINGS_DOWNLOAD_LOCATION
                   },
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
    )    

    copy_listings_to_raw_folder_task = PythonOperator(
        task_id="copy_listings_tar_file",
        python_callable=copy_listings_tar_file,
        op_kwargs={
                    "source_path": TMP_LISTINGS_SOURCE,
                    "destination_path": LOCAL_RAW_DATA_DIR,
                    "tar_file_name" : TAR_FILE_NAME
                   },
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
    )
    
    extract_listings_tar_task = PythonOperator(
        task_id="extract_tar_file",
        python_callable=extract_tar_file,
        op_kwargs={ 
                    "extract_dir_path": LOCAL_RAW_DATA_DIR, 
                    "tar_file": "abo-listings.tar", 
                    "local_extracted_json_dir": "listings/metadata/", 
                    "extracted_file_pattern": "listings_?.json.gz",
                    "decompressed_json_file_pattern": "listings_?.json"
                },
        #provide_context=True,        
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
        
    )
    
    flatten_all_listings_json_and_save_US_data_as_csv_task = PythonOperator(
        task_id="flatten_all_json_and_save_US_data_as_csv",
        python_callable=flatten_all_json_and_save_as_csv,
        op_kwargs= {"local_extracted_json_dir": "listings/metadata/"},
        provide_context=True,        
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
    )
    
    load_US_listings_data_task = PythonOperator(        
        task_id="load_us_data_and_perform_eda",
        python_callable=load_us_data_and_perform_eda,
        op_kwargs= {"local_tmp_dir": "listings/metadata/"},
        provide_context=True,        
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
    )

    perform_eda_on_US_listings_data_task = PythonOperator(        
        task_id="perform_eda_on_us_listings_data",
        python_callable=perform_eda_on_us_listings_data,
        op_kwargs= {"local_dir": "listings/metadata/"},
        provide_context=True,        
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
    )



  # Task 1: Download the images tar file
    # download_images_task = PythonOperator(
    #     task_id="download_tar_file_images",
    #     python_callable=download_tar_file_images,
    #     depends_on_past=False,
    #     dag=dag
    # )
    

    # check_if_image_file_arrived = S3KeySensor(
    #     task_id='check_if_data_file_arrived',
    #     poke_interval=10,  # Check for file every 60 seconds
    #     timeout=6000,  # Timeout if file not found after 600 seconds
    #     bucket_key=S3_OBJECT_KEY,  # Update with your S3 path
    #     bucket_name=AWS_S3_BUCKET,
    #     aws_conn_id="aws_default",
    #     mode='poke',
    #     dag=dag,
    # )

    copy_images_to_local_folder_from_s3_task = PythonOperator(
        task_id="copy_images_to_local_folder",
        python_callable=download_file_from_s3,
        task_concurrency=2,
        op_kwargs={
                    "bucket_name": AWS_S3_BUCKET,
                    "file_name" : IMAGES_OBJECT_S3_KEY_ID,
                    "local_file_path": TMP_IMAGE_DOWNLOAD_LOCATION
                   },
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
    )
    
    copy_to_rawimage_folder_task = PythonOperator(
        task_id="copy_to_rawimage_folder",
        python_callable=copy_file,
                op_kwargs={
                    "source_folder" : "/opt/airflow/downloads",                    
                    "destination_folder" : "/opt/airflow/data/rawimages",
                    "file_name": "abo-images-small.tar",
                  },       
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
        
    )
    # Task 2: Extract the images tar file
    extract_images_task = PythonOperator(
        task_id="extract_tar_file_images",
        python_callable=extract_tar_file_images,
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
    )

    # Task 3: Flatten the image metadata to a CSV file
    flatten_images_metadata_task = PythonOperator(
        task_id="flatten_to_csv_images",
        python_callable=flatten_to_csv_images,
        provide_context=True,
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
    )
    # Define task dependencies
    


    merge_listings_image_df_task = PythonOperator(
        task_id="merge_listings_image_df_task",
        op_kwargs= {"local_dir": "listings/metadata/"},
        python_callable=merge_listings_images,        
        provide_context=True,        
        trigger_rule='all_success',        
        dag=dag            
    )
    
    merged_data_clean_up_task = PythonOperator(
        task_id="merged_data_clean_up_task",
        python_callable=drop_if_image_file_missing,
        op_kwargs= {"local_dir": "listings/metadata/"},
        provide_context=True,
        trigger_rule='all_success',
        depends_on_past=False,
        dag=dag
    )
    
    #
    generate_image_captions_task = PythonOperator(
        task_id="generate_image_captions_task",
        op_kwargs= {"local_dir": "listings/metadata/"},
        python_callable=generate_image_captions,        
        provide_context=True,        
        trigger_rule='all_success',        
        dag=dag            
    )

    upload_captions_to_s3_task = PythonOperator(
        task_id="upload_captions_to_s3_task",
        op_kwargs= {
                    "bucket_name": AWS_S3_BUCKET,
                    "local_dir": "listings/metadata/"},
        python_callable=upload_captions_to_s3,        
        provide_context=True,        
        trigger_rule='all_success',        
        dag=dag            
    )
    
    check_if_data_file_arrived_task = S3KeySensor(
        task_id='check_if_data_file_arrived',
        poke_interval=10,  # Check for file every 60 seconds
        timeout=600,  # Timeout if file not found after 600 seconds
        bucket_key=S3_CAPTIONED_OBJECT_KEY,  # Update with your S3 path
        bucket_name=AWS_S3_BUCKET,
        aws_conn_id="aws_default",
        mode='poke',
        dag=dag,
    )

    load_faiss_vector_db_task = SimpleHttpOperator(
        task_id='load_faiss_vector_db_task',
        method='POST',
        http_conn_id=None,  # Define this connection in Airflow's Connection UI
        endpoint=FAISS_API_ENDPOINT,
        data=json.dumps({
            's3_bucket_name': AWS_S3_BUCKET,
            's3_object_key': S3_CAPTIONED_OBJECT_KEY
        }),
        headers={"Content-Type": "application/json"},
        response_check=lambda response: response.status_code == 200,  # Check success status
        extra_options={"timeout": 500},  # Timeout of 5 minutes -- Shouldn't take more than 3 mins    
    ) 
  
    
    
    # [download_task >> extract_task >> flatten_all_json_and_save_as_csv >>upload_listings_to_s3, download_images_task >> extract_images_task >> flatten_images_metadata_task] >> merge_listings_image_df_task
## If we are downloading and extracting the tar
#[download_task >> extract_task >> flatten_all_json_and_save_as_csv , download_images_task >> extract_images_task >> flatten_images_metadata_task] >> merge_listings_image_df_task

## If we are copying the tar file from local dir for minimal dataset
[copy_listings_from_s3 >> copy_listings_to_raw_folder_task >> extract_listings_tar_task >> flatten_all_listings_json_and_save_US_data_as_csv_task >> load_US_listings_data_task >> perform_eda_on_US_listings_data_task,  copy_images_to_local_folder_from_s3_task >> copy_to_rawimage_folder_task >> extract_images_task >> flatten_images_metadata_task] >> merge_listings_image_df_task >> merged_data_clean_up_task >> generate_image_captions_task >> upload_captions_to_s3_task >> check_if_data_file_arrived_task >> load_faiss_vector_db_task
#[check_if_data_file_arrived_task >> load_faiss_vector_db_task]
