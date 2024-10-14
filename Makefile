.PHONY: up down lint


up:
	sudo docker compose up -d
	python3 main.py

down:
	sudo docker compose down

lint:
	pylint ./ --recursive=true
