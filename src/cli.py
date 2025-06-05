import argparse

from data_processing.processing import process_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Run data processing pipeline")
    parser.add_argument('--input', required=True, help='Input file path or S3 key')
    parser.add_argument('--output', required=True, help='Output file path or S3 key')
    parser.add_argument('--bucket', help='S3 bucket name if using S3')
    args = parser.parse_args()

    use_s3 = args.bucket is not None
    process_file(args.input, args.output, use_s3=use_s3, bucket_name=args.bucket)


if __name__ == '__main__':
    main()
