import time
import requests
import numpy as np
from abc import ABC, abstractmethod


class ResponseProvider(ABC):
    """Abstract base class for email response providers"""

    @abstractmethod
    def generate_response(self, subject: str, body: str) -> str:
        """Generate a response to an email"""
        pass


class MockResponseProvider(ResponseProvider):
    """Mock response provider with simulated timing"""

    def __init__(self):
        self.response_counter = 0
        self.responses = [
            "Thank you for your email. I will get back to you shortly.",
            "I appreciate your message, and I'll respond as soon as possible.",
            "Your inquiry has been received. I'll review it and reply soon.",
            "Thanks for reaching out. Expect a detailed response shortly.",
        ]

    def generate_response(self, subject: str, body: str) -> str:
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


class OpenAIResponseProvider(ResponseProvider):
    """Real OpenAI API response provider"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def generate_response(self, subject: str, body: str) -> str:
        """Generate response using OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""You are a professional email assistant. Generate a helpful and concise response to this email.

Original Subject: {subject}
Original Message: {body}

Please provide a professional response:"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful email assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()

            response_data = response.json()
            message_content = response_data["choices"][0]["message"]["content"]

            return f"Re: {subject}\n\n{message_content.strip()}"

        except requests.RequestException as e:
            print(f"OpenAI API error: {e}")
            # Fallback to simple response
            return f"Re: {subject}\n\nThank you for your email. I'll get back to you soon."