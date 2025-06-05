# Endeavor Data Processing Example

This repository contains a small Python project
It demonstrates a data processing workflow that can read from local files or from
S3 (using LocalStack during development).

## Setup

1. Install dependencies:
   ```bash
   make setup
   ```
2. (Optional) start LocalStack if you want to test S3 integration:
   ```bash
   make run-localstack
   ```

## Running

Execute the CLI to process a file:

```bash
python -m cli --input input.txt --output output.txt
```

To use S3 via LocalStack:

```bash
AWS_ENDPOINT_URL=http://localhost:4566 \
python -m cli --input input-key --output output-key --bucket my-bucket
```

## Development

Run lint and tests:

```bash
make lint
make test
```
