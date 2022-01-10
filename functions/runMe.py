import boto3
import os

message = '''

Welcome to Altostra.

To set your name, send a request to POST /my-name with your name as the body.

See the README file for more detailed instructions on how to run this project locally and how to deploy it.

Happy Clouding!
'''

region = os.environ.get('AWS_REGION')
is_local = os.environ.get('AWS_SAM_LOCAL')
table_name = os.environ.get('TABLE_QUERYME01')

dynamo_db = is_local if None else boto3.client('dynamodb')

def handler(event, context):
    if event['httpMethod'] == 'GET':
        try:
            return {
                'statusCode': 200,
                'body': get_message(),
            }
        except BaseException as e:
            return {
                'statusCode': 500,
                'body': 'Unable to get the message due to a serverless error.',
            }
    elif event['httpMethod'] == 'POST':
        try:
            set_name(event['body'])
            return {
                'statusCode': 204,
            }
        except BaseException:
            return {
                'statusCode': 500,
                'body': 'Unable to set your name due to a serverless error.',
            }
    else:
        return {
            'statusCode': 400,
            'body': "It seems that you didn't provide the correct parameters :("
        }

def get_message():
    greeting = 'Hi!'

    if is_local:
        return greeting + message

    try:
        response = dynamo_db.get_item(
            TableName=table_name,
            Key={
                'pk': {
                    'S': 'SINGLETON',
                },
            }
        )

        
        if 'Item' in response and 'name' in response['Item']:
            greeting = 'Hi ' + response['Item']['name']['S'] + '!'
        else:
            greeting = 'Hi!'

        return greeting + message
    except BaseException as err:
        msg = 'Failed to get name from storage.'
        print(msg, err)

        raise

def set_name(name):
    if is_local:
        return
    
    try:
        if type(name) != str:
            raise TypeError('Provided name is invalid.')

        dynamo_db.put_item(
            TableName=table_name,
            Item={
                'pk': { 'S': 'SINGLETON' },
                'name': {'S': name},
            },
        )
    except BaseException as err:
        msg = 'Failed to store the name is storage.'
        print(msg, err)
        raise
