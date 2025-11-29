.PHONY: install run test docker-build docker-run

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest

docker-build:
	docker-compose build

docker-run:
	docker-compose up
