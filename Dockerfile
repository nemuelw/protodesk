# base image
FROM python:3.12-bullseye

# working directory
WORKDIR /app

# install required system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    patchelf

# copy project files
COPY . /app

# create and activate a virtual environment
RUN python -m venv .venv && chmod +x .venv/bin/activate && .venv/bin/activate

# install project dependencies
RUN pip3 install -r requirements.txt

# build the application with Nuitka
RUN nuitka --enable-plugin=pyside6 --include-data-dir=./assets=./assets --standalone --lto=yes --output-filename=protodesk app.py
