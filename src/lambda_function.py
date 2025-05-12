import json

def lambda_handler(event, context):
    # Print the incoming event for debugging
    print("Received event:", event)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello this is Lambda! From Amresh trying to deploy using CDK')
    }