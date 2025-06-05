import boto3
import pytest
from src.data_processing.processing import process_file


@pytest.fixture
def s3_client():
    """Create S3 client for LocalStack"""
    return boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )


def test_process_file_s3(s3_client):
    bucket_name = 'test-bucket'
    input_key = 'input.txt'
    output_key = 'output.txt'

    # Create bucket
    s3_client.create_bucket(Bucket=bucket_name)

    # Upload input file
    s3_client.put_object(Bucket=bucket_name, Key=input_key, Body=b'hello world')

    # Process file
    result = process_file(
        input_key, output_key, use_s3=True,
        bucket_name=bucket_name, s3_client=s3_client
    )

    # Verify result
    assert result == 'HELLO WORLD'

    # Verify output file in S3
    response = s3_client.get_object(Bucket=bucket_name, Key=output_key)
    assert response['Body'].read().decode('utf-8') == 'HELLO WORLD'
