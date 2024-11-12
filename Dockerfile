# base image
FROM python:3.12-slim

# working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    binutils \
    curl \
    gcc

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project files
COPY . /app

# add poetry to path
ENV PATH="/root/.local/bin:$PATH"

# install project dependencies
RUN poetry install --no-root

# build the application with Pyinstaller
RUN poetry run pyinstaller app.spec
