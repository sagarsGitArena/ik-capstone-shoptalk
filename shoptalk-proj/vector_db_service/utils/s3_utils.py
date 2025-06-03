import boto3
import logging
import os
from botocore.exceptions import NoCredentialsError

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def download_file_from_s3(bucket_name, s3_object_key, local_directory):
    """
    Downloads a file from an S3 bucket to a local directory.

    Parameters:
        aws_access_key (str): AWS access key ID.
        aws_secret_key (str): AWS secret access key.
        bucket_name (str): Name of the S3 bucket.
        s3_object_key (str): The full path to the object in the S3 bucket (key).
        local_directory (str): The local directory where the file will be downloaded.
    
    Returns:
        None
    """
    # Ensure the local directory exists
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    # Extract the file name from the S3 object key
    file_name = os.path.basename(s3_object_key)

    # Construct the local file path
    local_file_path = os.path.join(local_directory, file_name)

    # Create an S3 client
    # s3 = boto3.client('s3',                      
    #                     aws_access_key_id=aws_access_key,
    #                     aws_secret_access_key=aws_secret_key)

    s3 = boto3.client('s3')
                        
    print(f"Downloading '{s3_object_key}' from bucket '{bucket_name}' to '{local_file_path}'...")

    # Download the file
    try:
        s3.download_file(bucket_name, s3_object_key, local_file_path)
        print(f"File successfully downloaded to: {local_file_path}")
        return True
    except Exception as e:
        print(f"Error occurred while downloading: {e}")
    
    return False


def delete_file_from_s3(bucket_name, s3_object_key):
    """
    Downloads a file from an S3 bucket to a local directory and deletes the object from the S3 bucket.

    Parameters:
        aws_access_key (str): AWS access key ID.
        aws_secret_key (str): AWS secret access key.
        bucket_name (str): Name of the S3 bucket.
        s3_object_key (str): The full path to the object in the S3 bucket (key).
    Returns:
        None
    """

    # Create an S3 client
    # s3 = boto3.client('s3',
    #                   aws_access_key_id=aws_access_key,
    #                   aws_secret_access_key=aws_secret_key)
    s3 = boto3.client('s3')  

    try:
    
        # Step 1: Delete the file from S3
        print(f"Deleting '{s3_object_key}' from bucket '{bucket_name}'...")
        s3.delete_object(Bucket=bucket_name, Key=s3_object_key)
        print(f"File '{s3_object_key}' successfully deleted from bucket '{bucket_name}'.")
        return True
    except Exception as e:
        print(f"Error: {e}")
    
    return False


def upload_file_to_s3(bucket_name, file_name, local_file_path):
    # Create an S3 client using the provided credentials
    #s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    s3 = boto3.client('s3')

    try:
        # Upload the local file to the specified S3 bucket with the given filename
        s3.upload_file(local_file_path, bucket_name, file_name)
        print(f"File '{file_name}' uploaded successfully to '{bucket_name}'")
    except FileNotFoundError:
        print(f"The file '{local_file_path}' does not exist")
    except NoCredentialsError:
        print("Credentials not available or incorrect")
        
