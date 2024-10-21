.PHONY: up down lint


up:
	docker compose up -d

down:
	docker compose down

lint:
	pylint ./ --recursive=true

test:
	pytest --cov=. --cov-report term-missing
