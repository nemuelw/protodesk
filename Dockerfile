# base image
FROM python:3.12-slim

# working directory
WORKDIR /app

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project files
COPY . /app

# install project dependencies
RUN poetry install --no-root

# build the application with Pyinstaller
RUN poetry run pyinstaller app.spec
