.PHONY: setup lint test run-localstack test-email run-email

setup:
	pip install -r requirements.txt

lint:
	flake8 src tests *.py

test:
	pytest -v

run-localstack:
	docker-compose up -d localstack

test-email:
	python test_email_system.py

run-email:
	python email_cli.py --api-key $(API_KEY)
