import os
import boto3


def get_s3_client() -> boto3.client:
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    return boto3.client("s3", endpoint_url=endpoint_url)


def create_bucket(bucket_name: str) -> None:
    s3 = get_s3_client()
    existing = [b['Name'] for b in s3.list_buckets().get('Buckets', [])]
    if bucket_name not in existing:
        s3.create_bucket(Bucket=bucket_name)
