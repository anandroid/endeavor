#!/usr/bin/env python3
"""
Test script for the email response system
"""

import sys
import os
from src.email_processor import EmailResponseSystem

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_email_system():
    """Test the email system with a sample API key"""
    # Sample API key (replace with actual one)
    api_key = "apretzell0506"  # Example format

    print("Testing Email Response System")
    print(f"API Key: {api_key}")
    print("Running in test mode...")
    print("-" * 50)

    try:
        processor = EmailResponseSystem(api_key=api_key, test_mode=True)
        processor.run()

        print("\nTest completed successfully!")
        return True

    except Exception as e:
        print(f"Test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = test_email_system()
    sys.exit(0 if success else 1)
