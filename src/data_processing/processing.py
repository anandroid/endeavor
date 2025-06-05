import os
import boto3


def process_file(
    input_path: str,
    output_path: str,
    use_s3: bool = False,
    bucket_name: str | None = None,
) -> str:
    """Read data from input_path, convert to upper case and store at output_path.
    If use_s3 is True, input_path and output_path are keys within bucket_name.
    """
    if use_s3:
        endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
        s3 = boto3.client("s3", endpoint_url=endpoint_url)
        resp = s3.get_object(Bucket=bucket_name, Key=input_path)
        content = resp["Body"].read().decode("utf-8")
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    processed = content.upper()
    if use_s3:
        s3.put_object(Bucket=bucket_name, Key=output_path, Body=processed.encode("utf-8"))
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(processed)
    return processed
