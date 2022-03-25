import json
import boto3
import uuid
import argparse

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

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name=region)

## Create Dynamodb table
tablename = 'lex_intent_test_' + str(uuid.uuid4())
dynamotable = dynamodb.create_table(
                        AttributeDefinitions=[
                            {'AttributeName': 'Utterance', 'AttributeType': 'S',},
                            {'AttributeName': 'Intent','AttributeType': 'S',},
                        ],
                        KeySchema=[
                            { 'AttributeName': 'Utterance','KeyType': 'HASH'},
                            {'AttributeName': 'Intent','KeyType': 'RANGE'} 
                        ],
                        ProvisionedThroughput={'ReadCapacityUnits': 5,'WriteCapacityUnits': 5 },
                        TableName=tablename,
                    )

dynamotable.wait_until_exists()
print("[INFO]: DyanmoDB table created")

## get the bucket and object names
s3_objects = s3client.list_objects_v2(Bucket=bucket)

print("[INFO]: Processing the test data")
for s3_object in s3_objects.get('Contents'):
    
    ## process only the json
    if s3_object.get('Key').endswith('.json'):
        s3_file = s3client.get_object(Bucket=bucket,
                                       Key=s3_object.get('Key'))
        
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
                utternance = trans['Content']
                
                response = lexruntime.recognize_text(botId=botid,
                                                    botAliasId= botAliasId,
                                                    localeId=lang,
                                                    sessionId=session,
                                                    text=utternance)
                
                intent = response['sessionState']['intent']['name']
                
                print(f"utterance: {utternance} : intent: {intent}")
                
                dynamotable.put_item(Item =
                                    {'Utterance': utternance,
                                        'Intent': intent})

print("[INFO]: Successfully processed the test data")