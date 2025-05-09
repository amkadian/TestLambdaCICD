import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello this is Lambda! From Amresh trying to deploy using CDK')
    }