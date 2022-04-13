import json
import boto3
import argparse
import csv
import datetime

## parse the args
parser = argparse.ArgumentParser(description='Test your bot with a sample utterance')

parser.add_argument('--access_key', required=False, type=str, help="Access key credentials")
parser.add_argument('--secret_key', required=False, type=str, help="Secret key credentials ")
parser.add_argument('--region', required=False, default= 'us-east-1', help="Specify the region. ")
parser.add_argument('--bucket', required=False, help="Specify the test data bucket ")

parser.add_argument('--botid', required=True, type=str, help="Bot ID ")
parser.add_argument('--botaliasid', required=True, help="Bot Alias ID. ")

args = parser.parse_args()

## Set connection info
access_key = args.access_key
secret_key = args.secret_key
region = args.region
bucket = args.bucket

## Set bot info
botid = args.botid
botAliasId = args.botaliasid
session = 'test_session'
lang = 'en_US'

## get the boto3 clients
lexruntime = boto3.client('lexv2-runtime',
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name=region)

s3client = boto3.client('s3', 
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        region_name=region)

## get the bucket and object names
s3_objects = s3client.list_objects_v2(Bucket=bucket)

print("[INFO]: Processing the test data")

file_name = "lex_results_" + str(datetime.datetime.now()) + ".csv"

with open(file_name, 'wt') as out_file:
    csv_writer = csv.writer(out_file)
    csv_writer.writerow(['File Name', 'Utterance', 'Intent'])
    for s3_object in s3_objects.get('Contents'):
        
        ## process only the json
        if s3_object.get('Key').endswith('.json'):
            print("[INFO]: Processing the file: " + s3_object.get('Key'))
            s3_file = s3client.get_object(Bucket=bucket,
                                        Key=s3_object.get('Key'))
            
            source_filename = s3_object.get('Key')
            
            ## read the transcribed data file
            datafile = s3_file.get('Body').read().decode('utf-8')
            data = json.loads(datafile)

            ## find the participant id for the customer
            customer = 2
            for participant in data['Participants']:
                if participant['ParticipantRole'] == 'Customer' or participant['ParticipantRole'] == 'CUSTOMER':
                    customer = participant['ParticipantId']
                    
                ## loop thro the transcript
                for trans in data['Transcript']:
                    if trans['ParticipantId'] == customer:
                        utterance = trans['Content']
                        
                        response = lexruntime.recognize_text(botId=botid,
                                                            botAliasId= botAliasId,
                                                            localeId=lang,
                                                            sessionId=session,
                                                            text=utterance)
                        
                        intent = response['sessionState']['intent']['name']
                        
                        row = [source_filename, utterance, intent]
                                                
                        csv_writer.writerow(row)
                        
object_name = "output/" + file_name
response = s3client.upload_file(file_name, bucket, object_name)     
    
print("[INFO]: Successfully processed the test data")