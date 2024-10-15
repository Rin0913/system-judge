.PHONY: up down lint


up:
	sudo docker compose up -d

down:
	sudo docker compose down

lint:
	pylint ./ --recursive=true

test:
	pytest
