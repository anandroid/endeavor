#!/usr/bin/env python3
"""
Email Response System CLI
Run this script to process emails with dependency management.
"""

import argparse
import sys
from src.email_processor import EmailResponseSystem


def main():
    parser = argparse.ArgumentParser(description="Email Response System")
    parser.add_argument(
        "--api-key",
        required=True,
        help="API key in format: (first initial)(last name)(DDMM)"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        default=True,
        help="Run in test mode (default: True)"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Run in production mode (overrides test-mode)"
    )

    args = parser.parse_args()

    # Determine test mode
    test_mode = not args.production

    print("Starting Email Response System")
    print(f"API Key: {args.api_key}")
    print(f"Test Mode: {test_mode}")
    print("-" * 50)

    try:
        processor = EmailResponseSystem(api_key=args.api_key, test_mode=test_mode)
        results = processor.run()

        # Print final results
        successful = sum(1 for success in results.values() if success)
        total = len(results)

        print("\nFinal Results:")
        print(f"Successfully processed: {successful}/{total} emails")
        print(f"Success rate: {(successful/total)*100:.1f}%")

        if successful == total:
            print("✅ All emails processed successfully!")
            sys.exit(0)
        else:
            print("❌ Some emails failed to process")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
