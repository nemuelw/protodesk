FROM python:3.12-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y patchelf

COPY . /app

# create and activate a virtual environment
RUN python -m venv .venv && chmod +x .venv/bin/activate && .venv/bin/activate

# install project dependencies
RUN pip3 install -r requirements.txt

# build the app with Nuitka
RUN nuitka --enable-plugin=pyside6 --include-data-dir=./assets=./assets --standalone --onefile --lto=yes --output-filename=protodesk app.py
