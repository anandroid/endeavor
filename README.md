# Email Response System

An automated email processing system with dependency management, parallel execution, and timing constraints.

## Features

- **Dependency Graph Resolution**: Processes emails in correct order based on dependencies
- **Parallel Processing**: Handles independent emails concurrently for efficiency  
- **Timing Constraints**: Enforces deadlines and processes emails within time limits
- **OpenAI Integration**: Uses OpenAI API for generating intelligent email responses
- **Thread-Safe Operations**: Centralized completion tracking with locks

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key in `src/email_processor.py` (line 275):
   ```python
   openai_api_key = "your-openai-api-key-here"
   ```

3. Set your API key in `src/email_processor.py` (line 274):
   ```python
   api_key = "your-api-key-here"  # Format: (first initial)(last name)(DDMM)
   ```

## Usage

### Run the Email Processor

```bash
python src/email_processor.py
```

### API Key Format
Generate your API key using: `(first initial)(last name)(DDMM)`
- Example: For "Alice Smith" on December 15th: `asmith1512`

## Architecture

- **Core Logic**: `src/email_processor.py` - Main processing system with dependency resolution
- **Response Providers**: `src/response_providers.py` - OpenAI and mock response providers

## How It Works

1. Fetches emails from API endpoint with dependencies and deadlines
2. Builds dependency graph to determine processing order
3. Processes emails in parallel while respecting dependencies
4. Generates responses using OpenAI API
5. Sends responses back to the API endpoint
6. Tracks completion status and timing metrics