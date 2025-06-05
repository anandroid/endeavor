.PHONY: setup lint test run-localstack

setup:
	pip install -r requirements.txt

lint:
	flake8 src tests

test:
	pytest -v

run-localstack:
	docker-compose up -d localstack
