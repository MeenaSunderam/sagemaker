import boto3
import argparse
import os

## parse the args
parser = argparse.ArgumentParser(description='Test your Kendra with a Search Queries')

parser.add_argument('--access_key', required=False, type=str, help="Access key credentials")
parser.add_argument('--secret_key', required=False, type=str, help="Secret key credentials ")
parser.add_argument('--region', required=False, default= 'us-east-1', help="Specify the region. ")
parser.add_argument('--bucket', required=False, help="Specify the data bucket ")

args = parser.parse_args()

access_key = args.access_key
secret_key = args.secret_key
region = args.region
bucket = "aj-adp-ds-001"


## get the boto3 clients
s3client = boto3.resource('s3',
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name=region)

# Select Your S3 Bucket
s3bucket = s3client.Bucket(bucket)

for s3_object in s3bucket.objects.all():

    path, filename = os.path.split(s3_object.key)
    
    print(path)

    #Create sub directories if its not existing
    ##os.makedirs(path)
    
    #Download the file in the sub directories or directory if its available. 
    ##s3bucket.download_file(s3_object.key, path/filename)