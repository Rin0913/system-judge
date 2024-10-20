.PHONY: up down lint


up:
	docker compose up -d
	gunicorn --bind 0.0.0.0:8000 main:app

down:
	docker compose down

lint:
	pylint ./ --recursive=true

test:
	pytest --cov=. --cov-report term-missing
