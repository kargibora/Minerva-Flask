import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def create_s3_client(aws_access_key, aws_secret_key, region='us-west-2'):
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region,
    )
def upload_to_s3( bucket, s3_client, file_name = None, file_type = None, file = None, file_byte = None):
    # Reset the file's read position to the beginning
    if file is None and file_byte is None:
        raise ValueError("Either file or file_byte must be provided")
    
    if file is not None:
        file.seek(0)

    _file_name  = file.filename if file_name is None else file_name
    _file = file if file is not None else file_byte
    _file_content = file.content_type if file_type is None else file_type

    # Use the FileStorage object directly with the S3 client
    response = s3_client.put_object(
        Bucket=bucket,
        Key=_file_name,
        Body=_file,
        ContentType=_file_content
    )

    # Construct the file URL
    file_url = f"https://{bucket}.s3.amazonaws.com/{_file_name}"

    return file_url

def check_bucket_exists(bucket_name, aws_access_key, aws_secret_key, region='us-west-2'):
    """
    Check if the S3 bucket exists.

    :param bucket_name: str
        Name of the S3 bucket
    :param aws_access_key: str
        AWS access key
    :param aws_secret_key: str
        AWS secret key
    :param region: str, optional
        AWS region (default is 'us-west-2')
    :return: bool
        True if the bucket exists, False otherwise
    """
    try:
        s3_client = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        response = s3_client.head_bucket(Bucket=bucket_name)
        return response['ResponseMetadata']['HTTPStatusCode'] == 200
    except NoCredentialsError:
        print("No AWS credentials provided")
        return False
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Bucket '{bucket_name}' does not exist")
        else:
            print(f"Error occurred: {e}")
        return False
    