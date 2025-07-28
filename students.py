import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='ap-south-1')
dynamodbTableName = 'students'
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
studentsTable = dynamodb.Table(dynamodbTableName)

def lambda_handler(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:
        response = index_students_images(bucket, key)
        print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200 and response['FaceRecords']:
            faceID = response['FaceRecords'][0]['Face']['FaceId']
            name = key.split('.')[0].split('_')
            ernumber = name[0]
            firstName = name[1]
            register_employee(faceID, ernumber, firstName)
        return response
    except Exception as e:
        print(e)
        print(f'Error processing image {key} from bucket {bucket}')
        raise e

def index_students_images(bucket, key):
    response = rekognition.index_faces(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key,
            }
        },
        CollectionId="students"
    )
    return response

def register_employee(faceID, ernumber, firstName):
    studentsTable.put_item(
        Item={
            'recoginitionid': faceID,
            'ernumber': ernumber,
            'firstName': firstName
        }
    )
