import time
import threading
import requests
import heapq
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import concurrent.futures
from src.response_providers import ResponseProvider, MockResponseProvider, OpenAIResponseProvider


@dataclass
class Email:
    email_id: str
    subject: str
    body: str
    deadline: float
    dependencies: List[str]
    fetch_time: float


class EmailResponseSystem:
    def __init__(self, api_key: str, test_mode: bool = True,
                 response_provider: Optional[ResponseProvider] = None):
        self.api_key = api_key
        self.test_mode = test_mode
        self.completed_emails: Set[str] = set()
        self.completion_lock = threading.Lock()
        self.emails: Dict[str, Email] = {}
        self.dependency_graph: Dict[str, List[str]] = defaultdict(list)
        self.dependents_graph: Dict[str, List[str]] = defaultdict(list)
        self.dependency_count: Dict[str, int] = {}
        self.processing_queue: List[Tuple[float, str]] = []
        self.queue_lock = threading.Lock()
        self.processing_emails: Set[str] = set()  # Track emails being processed

        # Set up response provider
        if response_provider is None:
            self.response_provider = MockResponseProvider()
        else:
            self.response_provider = response_provider

        # API endpoints
        self.get_url = (
            "https://9uc4obe1q1.execute-api.us-east-2.amazonaws.com/dev/emails"
        )
        self.post_url = (
            "https://9uc4obe1q1.execute-api.us-east-2.amazonaws.com/dev/responses"
        )

    def fetch_emails(self) -> List[Email]:
        """Fetch emails from the GET endpoint"""
        params = {"api_key": self.api_key}
        if self.test_mode:
            params["test_mode"] = "true"

        response = requests.get(self.get_url, params=params)
        response.raise_for_status()

        emails_data = response.json()
        fetch_time = time.time()

        emails = []
        for email_data in emails_data:
            dependencies = []
            if email_data.get("dependencies"):
                dependencies = [
                    dep.strip() for dep in email_data["dependencies"].split(",")
                ]

            email = Email(
                email_id=email_data["email_id"],
                subject=email_data["subject"],
                body=email_data["body"],
                deadline=float(email_data["deadline"]),
                dependencies=dependencies,
                fetch_time=fetch_time
            )
            emails.append(email)

        return emails

    def build_dependency_graph(self, emails: List[Email]):
        """Build dependency graph and initialize processing queue"""
        self.emails = {email.email_id: email for email in emails}

        # Initialize dependency counts
        for email in emails:
            self.dependency_count[email.email_id] = len(email.dependencies)

            for dep_id in email.dependencies:
                self.dependency_graph[email.email_id].append(dep_id)
                self.dependents_graph[dep_id].append(email.email_id)

        # Add emails with no dependencies to processing queue
        for email in emails:
            if self.dependency_count[email.email_id] == 0:
                heapq.heappush(self.processing_queue,
                               (email.deadline, email.email_id))

    def get_ready_emails(self, max_batch_size: int = 80) -> List[str]:
        """Get batch of emails ready for processing from priority queue"""
        ready = []
        with self.queue_lock:
            # Get limited batch to avoid emptying entire queue
            batch_count = 0

            while self.processing_queue and batch_count < max_batch_size:
                deadline, email_id = heapq.heappop(self.processing_queue)
                if email_id not in self.completed_emails:
                    ready.append(email_id)
                    batch_count += 1
                # If email was already completed, continue to next

        return ready

    def mark_email_completed(self, email_id: str):
        """Mark email as completed and update dependency counts"""
        with self.completion_lock:
            self.completed_emails.add(email_id)

        # Update dependency counts for all dependents
        with self.queue_lock:
            for dependent_email_id in self.dependents_graph[email_id]:
                if dependent_email_id not in self.completed_emails:
                    self.dependency_count[dependent_email_id] -= 1

                    # If all dependencies are satisfied, add to processing queue
                    if self.dependency_count[dependent_email_id] == 0:
                        dependent_email = self.emails[dependent_email_id]
                        heapq.heappush(
                            self.processing_queue,
                            (dependent_email.deadline, dependent_email_id)
                        )

    def send_response(self, email_id: str, response_body: str) -> bool:
        """Send response via POST request"""
        payload = {
            "email_id": email_id,
            "response_body": response_body,
            "api_key": self.api_key
        }

        if self.test_mode:
            payload["test_mode"] = "true"

        try:
            response = requests.post(
                self.post_url,
                headers={"Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Failed to send response for {email_id}: {e}")
            return False

    def process_email(self, email_id: str) -> Tuple[bool, bool]:
        """Process a single email (generate and send response)"""
        email = self.emails[email_id]

        # Check if deadline has passed
        current_time = time.time()
        time_elapsed = current_time - email.fetch_time

        # Check if deadline has passed but still process to unblock dependents
        missed_deadline = time_elapsed >= email.deadline
        if missed_deadline:
            deadline_msg = (
                f"Email {email_id} missed deadline "
                f"({time_elapsed:.2f}s >= {email.deadline}s) - processing anyway"
            )
            print(deadline_msg)

        # Generate response
        response_body = self.response_provider.generate_response(
            email.subject, email.body)

        # Send response
        success = self.send_response(email_id, response_body)

        if success:
            status = "late" if missed_deadline else "on-time"
            print(f"Completed email {email_id} ({status})")
        else:
            print(f"Failed to process email {email_id}")

        return success, missed_deadline

    def process_emails_parallel(self) -> Dict[str, bool]:
        """Process all emails respecting dependencies and deadlines"""
        results = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=80) as executor:
            future_to_email = {}

            while len(self.completed_emails) < len(self.emails):
                # Get emails ready for processing
                ready_emails = self.get_ready_emails()

                if not ready_emails:
                    # Adaptive wait - longer when no emails ready
                    time.sleep(0.01)  # 10ms instead of 1ms
                    continue

                # Submit ready emails for processing (parallel response generation)
                for email_id in ready_emails:
                    if (email_id not in future_to_email and
                            email_id not in self.processing_emails and
                            email_id not in self.completed_emails):
                        self.processing_emails.add(email_id)
                        future = executor.submit(self.process_email, email_id)
                        future_to_email[future] = email_id

                # Batch process completed futures for efficiency
                completed_futures = []
                completed_emails_batch = []

                for future in future_to_email:
                    if future.done():
                        email_id = future_to_email[future]
                        try:
                            success, missed_deadline = future.result()
                            results[email_id] = success
                            completed_emails_batch.append((email_id, success))
                        except Exception as e:
                            print(f"Error processing email {email_id}: {e}")
                            results[email_id] = False
                            completed_emails_batch.append((email_id, False))
                        completed_futures.append(future)

                # Batch update completions to reduce lock contention
                for email_id, success in completed_emails_batch:
                    self.processing_emails.discard(email_id)  # Remove from processing set
                    self.mark_email_completed(email_id)

                # Clean up completed futures
                for future in completed_futures:
                    del future_to_email[future]

                # Check if all emails are processed
                if len(results) == len(self.emails):
                    break

        return results

    def run(self) -> Dict[str, bool]:
        """Main execution function"""
        print(f"Fetching emails with API key: {self.api_key}")
        emails = self.fetch_emails()
        print(f"Fetched {len(emails)} emails")

        self.build_dependency_graph(emails)
        print("Built dependency graph")

        results = self.process_emails_parallel()

        # Print summary
        successful = sum(1 for success in results.values() if success)
        total_results = len(results)
        print(f"\nResults: {successful}/{len(emails)} emails processed")
        if total_results != len(emails):
            print(f"WARNING: Results count ({total_results}) != Email count ({len(emails)})")
            if total_results > len(emails):
                print("Possible duplicate processing detected!")

        return results


def main():
    # Generate API key (replace with your actual key)
    api_key = "anandkumar0506"
    openai_api_key = "";

    # Choose response provider
    # Option 1: Use mock responses (default)
    mock_provider = MockResponseProvider()
    openai_provider = OpenAIResponseProvider(openai_api_key)
    processor = EmailResponseSystem(api_key=api_key, test_mode=False,
                                    response_provider=openai_provider)

    # Option 2: Use real OpenAI API (uncomment below)
    # openai_api_key = "your-openai-api-key-here"
    # openai_provider = OpenAIResponseProvider(openai_api_key)
    # processor = EmailResponseSystem(api_key=api_key, test_mode=True,
    #                                 response_provider=openai_provider)

    results = processor.run()
    return results


if __name__ == "__main__":
    main()
