
import boto3
from botocore.exceptions import NoCredentialsError

import boto3
from botocore.exceptions import NoCredentialsError


#def upload_file_to_s3(access_key, secret_key, bucket_name, file_name, local_file_path):
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
        


#def download_file_from_s3(access_key, secret_key, bucket_name, file_name, local_file_path):
def download_file_from_s3( bucket_name, file_name, local_file_path):
    #print(f'AWS_ACCESS_KEY:{access_key}, AWS_SECRET_KEY:{secret_key}')
    #s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    s3 = boto3.client('s3')

    try:
        s3.download_file(bucket_name, file_name, local_file_path)
        print(f"File '{file_name}' downloaded successfully to '{local_file_path}'")
    except FileNotFoundError:
        print(f"The file '{file_name}' does not exist in the bucket '{bucket_name}'")
    except NoCredentialsError:
        print("Credentials not available or incorrect")        

#def copy_file_between_buckets(access_key, secret_key, source_bucket, destination_bucket, file_name):
def copy_file_between_buckets(source_bucket, destination_bucket, file_name):
    # Create an S3 client using the provided credentials
    #s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    s3 = boto3.client('s3')

    try:
        # Copy the object (file) from the source bucket to the destination bucket
        copy_source = {'Bucket': source_bucket, 'Key': file_name}
        s3.copy_object(Bucket=destination_bucket, CopySource=copy_source, Key=file_name)
        
        print(f"File '{file_name}' copied successfully from '{source_bucket}' to '{destination_bucket}'")
    except NoCredentialsError:
        print("Credentials not available or incorrect")        
    


