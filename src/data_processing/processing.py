from typing import Optional
from utils.s3_utils import get_s3_client


def process_file(
    input_path: str,
    output_path: str,
    use_s3: bool = False,
    bucket_name: Optional[str] = None,
    s3_client=None,
) -> str:
    """Read data from input_path, convert to upper case and store at output_path.
    If use_s3 is True, input_path and output_path are keys within bucket_name.
    """
    if use_s3:
        s3 = s3_client or get_s3_client()
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


class DataProcessingService:
    def __init__(self, s3_client=None):
        self.s3_client = s3_client or get_s3_client()

    def process_file(
        self,
        input_path: str,
        output_path: str,
        use_s3: bool = False,
        bucket_name: Optional[str] = None,
    ) -> str:
        """Process file using the service's S3 client."""
        return process_file(
            input_path=input_path,
            output_path=output_path,
            use_s3=use_s3,
            bucket_name=bucket_name,
            s3_client=self.s3_client if use_s3 else None,
        )
