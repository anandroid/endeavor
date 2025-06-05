# Endeavor Data Processing & Email Response System

This repository contains two main components:

1. **Data Processing Pipeline**: Demonstrates clean architecture patterns with dual local file and S3 support
2. **Email Response System**: Automated email processing with dependency management and parallel execution

## Data Processing Pipeline

The data processing pipeline converts text to uppercase and showcases dependency injection, service layer patterns, and modular design.

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

## Email Response System

An automated system that processes emails with dependency management, parallel execution, and timing constraints.

### Features

- **Dependency Graph Resolution**: Processes emails in correct order based on dependencies
- **Parallel Processing**: Handles independent emails concurrently for efficiency
- **Timing Constraints**: Enforces deadlines and 100μs gaps between dependent responses
- **Mock LLM Integration**: Simulates OpenAI response times (0.4-0.6 seconds)
- **Thread-Safe Operations**: Centralized completion tracking with locks

### Email System Usage

#### Test Mode (Recommended for Development)

```bash
# Test with sample API key (replace with your key: first_initial + last_name + DDMM)
python email_cli.py --api-key apretzell0506 --test-mode

# Or use the make command
make test-email
```

#### Production Mode

```bash
# Production run (processes full email stream with strict deadlines)
python email_cli.py --api-key YOUR_API_KEY --production

# Or with make command
make run-email API_KEY=YOUR_API_KEY
```

#### API Key Format
Generate your API key using: `(first initial)(last name)(DDMM)`
- Example: For "Alice Smith" on December 15th: `asmith1512`

### Email System Architecture

- **Entry Point**: `email_cli.py` - Command-line interface
- **Core Logic**: `src/email_processor.py` - Main processing system with dependency resolution
- **Test Script**: `test_email_system.py` - System validation

## Development

Run lint and tests:

```bash
make lint
make test
```

Available make commands:
```bash
make setup          # Install all dependencies
make lint           # Run code linting
make test           # Run pytest tests
make run-localstack # Start LocalStack for S3 testing
make test-email     # Test email response system
make run-email      # Run email system (requires API_KEY variable)
```
