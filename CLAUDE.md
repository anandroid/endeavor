# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Setup**: `make setup` - Install Python dependencies
- **Lint**: `make lint` - Run flake8 on src and tests directories
- **Test**: `make test` - Run pytest with verbose output
- **Run single test**: `pytest tests/test_processing.py::test_process_file -v`
- **CLI execution**: `python -m cli --input <input> --output <output> [--bucket <bucket>]`

## LocalStack S3 Testing

- **Start LocalStack**: `make run-localstack` - Starts LocalStack on port 4566
- **S3 CLI usage**: Set `AWS_ENDPOINT_URL=http://localhost:4566` environment variable

## Architecture

This is a data processing pipeline with dual file/S3 support:

- **Entry point**: `src/cli.py` - Command-line interface that determines local vs S3 mode based on `--bucket` parameter
- **Core processing**: `src/data_processing/processing.py` - Contains `process_file()` function that handles both local file and S3 operations in a single interface
- **S3 utilities**: `src/utils/s3_utils.py` - Helper functions for S3 client creation and bucket management
- **AWS configuration**: Uses `AWS_ENDPOINT_URL` environment variable to switch between LocalStack (development) and real AWS S3

The processing logic is intentionally simple (uppercase conversion) to focus on demonstrating the dual local/S3 architecture pattern.