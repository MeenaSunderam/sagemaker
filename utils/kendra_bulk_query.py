import boto3
import argparse
import datetime
import csv

## parse the args
parser = argparse.ArgumentParser(description='Test your Kendra with a Search Queries')

parser.add_argument('--access_key', required=False, type=str, help="Access key credentials")
parser.add_argument('--secret_key', required=False, type=str, help="Secret key credentials ")
parser.add_argument('--region', required=False, default= 'us-east-1', help="Specify the region. ")

parser.add_argument('--bucket', required=False, help="Specify the data bucket ")
parser.add_argument('--object', required=False, help="Specify the data Object ")
parser.add_argument('--file', required=False, help="Specify the file in your local directory")

parser.add_argument('--index_id', required=True, type=str, help="Kendra Index ID ")
args = parser.parse_args()

## Set connection info
access_key = args.access_key
secret_key = args.secret_key
region = args.region
bucket = args.bucket
object = args.object

kendra_indexid = args.index_id
#kendra_indexid = 'fecbcae4-f043-4fbf-8fc0-e5e8f65c6fdd'

## get the boto3 clients
kendraclient = boto3.client('kendra',
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name=region)

s3client = boto3.client('s3', 
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        region_name=region)

if args.file:
    input_file = args.file
    print("[INFO]: Reading the Input data - Using the file mode")
elif args.object:
    input_file = s3client.get_object(Bucket=bucket, Key=object)
    print("[INFO]: Reading the Input data - Using S3 Object mode")

data = {}
with open(input_file) as file:
    for row in csv.DictReader(file):
        for key, values in row.items():
            if key not in data:
                data[key] = []
            data[key].append(values)

print("[INFO]: Processing the test data")
file_name = "kendra_results" + str(datetime.datetime.now()) + ".csv"

with open(file_name, 'wt') as out_file:
    csv_writer = csv.writer(out_file)
    csv_writer.writerow(["query_text", "answer_text", "document_title", "document_text", "document_url"])
    
    for data_item in data['query']:      
        #for row in df.values:
        query_text = data_item
        
        print("[INFO]: Processing utterance: " + query_text)
        
        response = kendraclient.query(
            IndexId=kendra_indexid,
            QueryText=query_text,
        )
        
        for query_result in response['ResultItems'][:5]:

            #print('-------------------')
            #print('Type: ' + str(query_result['Type']))
            
            answer_text = ""
            if query_result['Type']=='ANSWER' or query_result['Type'] == 'QUESTION_ANSWER':
                answer_text = query_result['DocumentExcerpt']['Text']
                #print(answer_text)
                
            document_text =""
            document_url = ""
            document_title = ""
            
            if query_result['Type']=='DOCUMENT':
                if 'DocumentTitle' in query_result:
                    document_title = query_result['DocumentTitle']['Text']
                    #print('Title: ' + document_title)
                document_text = query_result['DocumentExcerpt']['Text']
                document_url = query_result['DocumentURI']
                #print(document_text)

            csv_writer.writerow([query_text, answer_text, document_title, document_text, document_url])
  
## Save the file in S3 
if args.bucket:
    s3client.upload_file(file_name, args.bucket, file_name)
    print("[INFO]: File saved in S3 bucket: " + args.bucket)                       
    
print("[INFO]: Successfully processed the Kendra Job")