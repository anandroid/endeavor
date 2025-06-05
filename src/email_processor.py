import time
import threading
import requests
import numpy as np
from typing import Dict, List, Set
from dataclasses import dataclass
from collections import defaultdict
import concurrent.futures


@dataclass
class Email:
    email_id: str
    subject: str
    body: str
    deadline: float
    dependencies: List[str]
    fetch_time: float


class EmailResponseSystem:
    def __init__(self, api_key: str, test_mode: bool = True):
        self.api_key = api_key
        self.test_mode = test_mode
        self.completed_emails: Set[str] = set()
        self.completion_lock = threading.Lock()
        self.emails: Dict[str, Email] = {}
        self.dependency_graph: Dict[str, List[str]] = defaultdict(list)
        self.dependents_graph: Dict[str, List[str]] = defaultdict(list)
        self.potentially_ready_emails: Set[str] = set()
        self.response_counter = 0
        self.responses = [
            "Thank you for your email. I will get back to you shortly.",
            "I appreciate your message, and I'll respond as soon as possible.",
            "Your inquiry has been received. I'll review it and reply soon.",
            "Thanks for reaching out. Expect a detailed response shortly.",
        ]

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
        """Build dependency graph from emails"""
        self.emails = {email.email_id: email for email in emails}

        for email in emails:
            for dep_id in email.dependencies:
                self.dependency_graph[email.email_id].append(dep_id)
                self.dependents_graph[dep_id].append(email.email_id)

            # Initialize potentially ready emails with those having no dependencies
            if not email.dependencies:
                self.potentially_ready_emails.add(email.email_id)

    def get_ready_emails(self) -> List[str]:
        """Get emails that have no pending dependencies (optimized graph version)"""
        ready = []
        emails_to_remove = set()

        # Only check emails in potentially_ready_emails set
        for email_id in self.potentially_ready_emails.copy():
            if email_id in self.completed_emails:
                emails_to_remove.add(email_id)
                continue

            email = self.emails[email_id]
            # Check if all dependencies are completed
            all_deps_completed = all(
                dep_id in self.completed_emails
                for dep_id in email.dependencies
            )

            if all_deps_completed:
                ready.append(email_id)
                emails_to_remove.add(email_id)

        # Remove processed emails from potentially ready set
        self.potentially_ready_emails -= emails_to_remove
        return ready

    def mark_email_completed(self, email_id: str):
        """Mark email as completed and update potentially ready emails"""
        with self.completion_lock:
            self.completed_emails.add(email_id)

            # Add all dependents of this email to potentially ready set
            for dependent_email_id in self.dependents_graph[email_id]:
                if dependent_email_id not in self.completed_emails:
                    self.potentially_ready_emails.add(dependent_email_id)

    def mock_openai_response(self, subject: str, body: str) -> str:
        """Mock OpenAI response with timing constraints"""
        # Generate delay between 0.4 and 0.6 seconds
        delay = np.random.exponential(scale=0.5)
        delay = max(0.4, min(delay, 0.6))
        time.sleep(delay)
        # Cycle through responses
        response_text = self.responses[
            self.response_counter % len(self.responses)
        ]
        self.response_counter += 1

        return f"Re: {subject}\n\n{response_text}"

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

    def process_email(self, email_id: str) -> bool:
        """Process a single email"""
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
        response_body = self.mock_openai_response(email.subject, email.body)

        # Send response
        success = self.send_response(email_id, response_body)

        if success:
            # Mark as completed and update graph
            self.mark_email_completed(email_id)

            # Wait 100 microseconds before allowing dependent emails
            time.sleep(0.0001)

            status = "late" if missed_deadline else "on-time"
            print(f"Completed email {email_id} ({status})")
            return True

        return False

    def process_emails_parallel(self) -> Dict[str, bool]:
        """Process all emails respecting dependencies and deadlines"""
        results = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_email = {}

            while len(self.completed_emails) < len(self.emails):
                # Get emails ready for processing
                ready_emails = self.get_ready_emails()

                if not ready_emails:
                    # Wait a bit and check again
                    time.sleep(0.001)
                    continue

                # Submit ready emails for processing
                for email_id in ready_emails:
                    if email_id not in future_to_email:
                        future = executor.submit(self.process_email, email_id)
                        future_to_email[future] = email_id

                # Check completed futures
                completed_futures = []
                for future in future_to_email:
                    if future.done():
                        email_id = future_to_email[future]
                        try:
                            result = future.result()
                            results[email_id] = result
                        except Exception as e:
                            print(f"Error processing email {email_id}: {e}")
                            results[email_id] = False
                        completed_futures.append(future)

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
        print(f"\nResults: {successful}/{len(emails)} emails processed")

        return results


def main():
    # Generate API key (replace with your actual key)
    api_key = "apretzell0506"  # Example: first initial + last name + DDMM

    # Create and run email processor
    processor = EmailResponseSystem(api_key=api_key, test_mode=True)
    results = processor.run()

    return results


if __name__ == "__main__":
    main()
