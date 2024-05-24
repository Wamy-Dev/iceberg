.PHONY: help install run start stop logs clean format lint test pr-ready

# Detect operating system
ifeq ($(OS),Windows_NT)
    # For Windows
    DATA_PATH := $(shell echo %cd%)\data
else
    # For Linux
    DATA_PATH := $(PWD)/data
endif

help:
	@echo Iceberg Local Development Environment
	@echo -------------------------------------------------------------------------
	@echo install   : Install the required packages
	@echo run       : Run the Iceberg backend
	@echo start     : Build and run the Iceberg container \(requires Docker\)
	@echo stop      : Stop and remove the Iceberg container \(requires Docker\)
	@echo logs      : Show the logs of the Iceberg container \(requires Docker\)
	@echo clean     : Remove all the temporary files
	@echo format    : Format the code using isort
	@echo check     : Check the code using pyright
	@echo lint      : Lint the code using ruff and isort
	@echo test      : Run the tests using pytest
	@echo coverage  : Run the tests and generate coverage report
	@echo pr-ready  : Run the linter and tests
	@echo -------------------------------------------------------------------------

# Docker related commands

start: stop
	@docker build -t iceberg:latest -f Dockerfile .
	@docker run -d --name iceberg --hostname iceberg --net host -e PUID=1000 -e PGID=1000 -v $(DATA_PATH):/iceberg/data -v /mnt:/mnt iceberg:latest
	@docker logs iceberg -f

stop:
	@-docker stop iceberg --time 0
	@-docker rm iceberg --force
	@-docker rmi iceberg:latest --force

logs:
	@docker logs iceberg -f

# Poetry related commands

clean:
	@find . -type f -name '*.pyc' -exec rm -f {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '.pytest_cache' -exec rm -rf {} +
	@find . -type d -name '.ruff_cache' -exec rm -rf {} +
	@rm -rf data/media.pkl data/media.pkl.bak

install:
	@poetry install --with dev

# Run the application
run:
	@poetry run python backend/main.py

# Code quality commands
format:
	@poetry run isort backend

check:
	@poetry run pyright

lint:
	@poetry run ruff check backend
	@poetry run isort --check-only backend

sort:
	@poetry run isort backend

test:
	@poetry run pytest backend

coverage: clean
	@poetry run pytest backend --cov=backend --cov-report=xml --cov-report=term

# Run the linter and tests
pr-ready: clean lint test
