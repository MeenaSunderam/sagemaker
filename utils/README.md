# AWS AI Services Utilities

**Disclaimer**:

1.  Please avoid passing access_key and secrete_key as arguments as security best practice. We can recommend running the script on AWS Shell or any other CLI that has AWS access configured (could be Cloud9, or EC2 with appropriate IAM role)

2.  These utilities should be used for testing purposes during your development efforts NOT in any production environment

3.  If this is used with 300+ queries, it will likely get into throttling issues which the script needs to handle (for developer edition the query capacity is 4000 queries per day i.e. about 0.05 queries per second or 3 queries per minute, by default the Enterprise Edition index the capacity is double of this)

## Kendra Utility

### Purpose:
Bulk test search query strings on Amazon Kendra.  You provide a csv with a list of search queries, the utility parses the csv, queries Amazon Kendra and captures the result in a result csv.  
You can have the csv.  
- in your local folder 
- or in an s3 bucket

### Usage:

python3 kendra_bulk_query.py --access_key <<Access key>>  --secret_key <<Secret key>> --region <<Region>> --bucket <<Bucket>> --object <<Object>> --file <<file>> --index_id <<Index ID>>

## Lex Utility

### Purpose:
Bulk test Lex intent detection.  Utility uses the json files from the transcriptions from a s3 folder, processes the same in lex and saves the intents from lex in a csv file
  
### Usage:

python3 lex_bulk_intents_from_transcriptions.py --access_key <<Access key>>  --secret_key <<Secret key>> --region <<Region>> --bucket <<Bucket>> --botid <<BotID>> --botaliasid <<bot alias id>>
