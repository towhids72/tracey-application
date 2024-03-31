FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /home/app

WORKDIR /home/app
RUN mkdir -p /home/app/.database

COPY ./pyproject.toml ./poetry.lock* ./

RUN pip install poetry
RUN poetry install --no-root

COPY . /home/app
