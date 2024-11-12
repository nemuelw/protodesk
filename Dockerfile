# base image
FROM python:3.12-slim

# working directory
WORKDIR /app

# install required system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    patchelf

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project files
COPY . /app

# add poetry to path
ENV PATH="/root/.local/bin:$PATH"

# activate poetry environment
RUN poetry shell

# install project dependencies
RUN poetry install --no-root

# build the application with Nuitka
RUN poetry run nuitka --enable-plugin=pyside6 --include-data-dir=./assets=./assets --standalone --lto=yes --output-filename=protodesk app.py
