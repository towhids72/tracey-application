# Tracey Transform API
[![forthebadge made-with-python](https://forthebadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-390/) [![Docker](https://badgen.net/badge/icon/docker?icon=docker&label)](https://https://docker.com/)

## Contents
- [What does this project do?](#what-does-this-project-do)
- [Before you begin](#before-you-begin)
- [How to run the project](#how-to-run-the-project)
- [How to run tests](#how-to-run-tests)
- [mypy checks](#mypy-checks)

## What does this project do?
The Tracey API streamlines shipment tracking by collecting data from various carriers such as DHL, BPOST, and more, 
and converting it into a standardized Tracey format.

## Before you begin
Before you begin, please follow these steps:

1. Put `filtered_events.json` file in the root directory of your project.
2. Create a directory named `secrets` in the root directory of your project.
3. Move the `.env.template` file into the `secrets` directory you just created.
4. Create two copies of the `.env.template` file within the `secrets` directory.
5. Rename one copy to `.env` and the other copy to `.env.docker`.
6. Update the variables in the `.env` file according to your local environment.
7. Update the variables in the `.env.docker` file according to your docker environment.


## How to Run the Project
Navigate to the root of the project. <br>
To build the image from the Dockerfile, run:
```commandline
docker compose up --build -d
```

<br>Or, If you want to run the project locally, you need to have `poetry` installed first.
```commandline
pip install poetry
poetry install --no-root
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

<br>Or, there's a `Makefile` for your convenience, so just run: (Check other commands too!)
```
make run
```

<br>Now, you can check the **Swagger** URL for API documentation.
```
http://localhost:8000
```

## How to run tests
Use _pytest_ command to run the tests.<br>

Using docker:
```
docker exec -it tracey_api poetry run pytest
```

In your local:
```
poetry run pytest
```

Using make:
```
make tests
```

<br>And, You can check the coverage as well:

Using docker:
```
docker exec -it tracey_api poetry run coverage run -m pytest
docker exec -it tracey_api poetry run coverage report

# Backend Directory               Stmts   Miss  Cover
# -----------------------------------------------------
# Test Coverage TOTAL              498     31    94%
```

In your local:
```
poetry run coverage run -m pytest
poetry run coverage report
```

Using make:
```
make coverage
```

## mypy checks
<br>This project has been thoroughly checked with `mypy` for type consistency, and it currently passes all 
mypy checks without any issues.

For running mypy, just run:

Using docker:
```
docker exec -it tracey_api poetry run mypy .
```

Running it locally:
```
poetry run mypy .
```

Using make:
```
make mypy
```