# AGENTS Instructions

This repository hosts a sample data processing pipeline. The code supports local file
processing and optional S3 integration using LocalStack.

## Required Setup

- Run `make setup` to install Python dependencies.
- Run `make lint` to check code style with flake8.
- Run `make test` to execute the unit tests.
- Optional: start LocalStack with `make run-localstack` to emulate AWS services.

## Programmatic Checks

Before committing code, run `make lint` and `make test` and ensure both succeed.
