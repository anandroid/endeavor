# Endeavor Data Processing Example

This repository contains a data processing pipeline that demonstrates clean architecture patterns with dual local file and S3 support. The pipeline converts text to uppercase and showcases dependency injection, service layer patterns, and modular design.

## Architecture

- **Service Layer**: `DataProcessingService` class provides a clean interface for data processing operations
- **Dependency Injection**: S3 clients can be injected for testing and flexibility
- **Dual Mode Support**: Seamlessly handles both local files and S3 objects
- **Modular Design**: Separated utilities, processing logic, and CLI interface

## Setup

1. Install dependencies:
   ```bash
   make setup
   ```
2. (Optional) start LocalStack if you want to test S3 integration:
   ```bash
   make run-localstack
   ```

## Usage

### Local File Processing

Process a local file (converts text to uppercase):

```bash
python -m cli --input input.txt --output output.txt
```

### S3 Processing with LocalStack

Process files stored in S3 using LocalStack for development:

```bash
# Set LocalStack endpoint
export AWS_ENDPOINT_URL=http://localhost:4566

# Process S3 objects
python -m cli --input input-key --output output-key --bucket my-bucket
```

### S3 Processing with AWS

Process files in real AWS S3 (requires AWS credentials):

```bash
# Unset LocalStack endpoint to use real AWS
unset AWS_ENDPOINT_URL

# Process S3 objects
python -m cli --input path/to/input.txt --output path/to/output.txt --bucket production-bucket
```

### CLI Parameters

- `--input`: Input file path (local) or S3 key
- `--output`: Output file path (local) or S3 key  
- `--bucket`: S3 bucket name (optional, triggers S3 mode when provided)

## Development

Run lint and tests:

```bash
make lint
make test
```
