import boto3
import json

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='ap-south-1')
dynamodbTableName = 'students'
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
studentsTable = dynamodb.Table(dynamodbTableName)
bucketname = 'student-attendance-img'

def lambda_handler(event, context):
    print(event)
    objectKey = event['queryStringParameters']['objectkey']
    image_bytes = s3.get_object(Bucket=bucketname, Key=objectKey)['Body'].read()
    respose = rekognition.search_faces_by_image(
        CollectionId='employees',
        Image={'Bytes':image_bytes}
    )

    for match in respose['FaceMatches']:
        print(match['Face']['FaceId'],match['Face']['Confidence'])

        face = studentsTable.get_item(
            Key={
                'rekognitionId' : match['Face']['FaceId']
            }
        )
        if 'Item' in face:
            print('Person Found: ', face['Item'])
            return buildResponse(200, {
                'Message' : 'Success',
                'ernumber' : face['Item']['ernumber'],
                'firstName' : face['Item']['firstName']
            })
        print('Student could not be present')
    return buildResponse(403, {'Meesage' : 'Student Not Found'})
def buildResponse(statusCode, body=None):
    response = {
        'statusCode' : statusCode,
        'headers' : {
            'Content-Type' : 'application/json',
            'Access-Control-Allow-Origin':'*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response