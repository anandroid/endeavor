# Email Response System

An automated email processing system that efficiently handles large-scale email processing with dependency management, parallel execution, and intelligent response generation.

## Key Implementation Features

### Dependency Graph Management
- **Graph Construction**: The system builds bidirectional dependency graphs (`dependency_graph` and `dependents_graph`) from email relationships, tracking which emails depend on others and which emails are waiting for dependencies to complete
- **Dynamic Dependency Resolution**: When an email is processed, the system decrements dependency counts for all dependent emails (`mark_email_completed:124-134`) and automatically adds newly-ready emails to the processing queue
- **Priority Queue Processing**: Uses a min-heap (`heapq`) to prioritize emails by deadline, ensuring the most urgent emails are processed first (`get_ready_emails:101-115`)

### High-Scale Parallel Processing
- **ThreadPoolExecutor**: Employs a thread pool with 80 concurrent workers (`process_emails_parallel:195`) to handle response generation and API calls in parallel
- **Batch Processing**: Processes emails in configurable batches (max 80 per batch) to balance throughput and resource usage while avoiding queue exhaustion
- **Thread-Safe Operations**: Uses locks (`completion_lock`, `queue_lock`) to ensure safe concurrent access to shared data structures
- **Adaptive Processing**: Implements tracking of emails in different states (processing, completed) to prevent duplicate work and optimize resource allocation

### Intelligent Response Generation
- **OpenAI Integration**: The `OpenAIResponseProvider` generates contextual email responses using GPT-3.5-turbo with professional prompting (`response_providers.py:52-88`)
- **Fallback Mechanism**: Includes error handling with graceful degradation to simple responses if OpenAI API fails
- **Response Timing**: Optimized for real-world API response times while maintaining deadline compliance

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure API keys in `src/email_processor.py`:
   ```python
   api_key = "your-api-key-here"  # Format: (first initial)(last name)(DDMM)
   openai_api_key = "your-openai-api-key-here"
   ```

## Usage

### Run the Email Processor

```bash
python src/email_processor.py
```

### API Key Format
Generate the API key using: `(first initial)(last name)(DDMM)`
- Example: For "Alice Smith" on December 15th: `asmith1512`

## Architecture

### Core Components
- **EmailResponseSystem** (`src/email_processor.py`): Main orchestrator handling dependency resolution, parallel processing, and email lifecycle management
- **Response Providers** (`src/response_providers.py`): Abstracted response generation with OpenAI integration and mock provider for testing
- **Email Dataclass**: Structured email representation with deadline, dependency, and timing information

### Processing Flow
1. **Email Fetching**: Retrieves emails from REST API with dependency and deadline metadata
2. **Graph Construction**: Builds dependency graphs and initializes processing queue with emails having no dependencies
3. **Parallel Processing**: Continuously polls for ready emails, submits them to thread pool, and processes completions in batches
4. **Response Generation**: Uses OpenAI API to generate contextual responses based on email subject and body
5. **Completion Handling**: Updates dependency counts, unlocks dependent emails, and tracks processing statistics
6. **Result Reporting**: Provides comprehensive metrics on processing success rates and timing performance