FROM python:3.12-bullseye

ARG APP_VERSION
ARG ARCH
# ENV APP_VERSION=${APP_VERSION}
# ENV ARCH=${ARCH}

WORKDIR /app

RUN apt-get update && apt-get install -y patchelf desktop-file-utils libfuse2

COPY . /app

# create and activate a virtual environment
RUN python -m venv .venv && chmod +x .venv/bin/activate && .venv/bin/activate

# install project dependencies
RUN pip install -r requirements.txt

# build the app with Nuitka
RUN nuitka --enable-plugin=pyside6 --include-data-dir=./assets=./assets --standalone --onefile --lto=yes --output-filename=protodesk app.py

# prepare AppImage directory
RUN mkdir -p app.AppDir/usr/bin
RUN cp protodesk app.AppDir/usr/bin/
RUN cp assets/logo.png app.AppDir/protodesk.png

# set up appimagetool
RUN bash -c "\
    if [ "$(uname -m)" == "x86_64" ]; then \
        wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool; \
    elif [ "$(uname -m)" == "aarch64" ]; then \
        wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-aarch64.AppImage -O appimagetool; \
    fi && \
    chmod +x appimagetool \
    "

# build the AppImage
RUN ./appimagetool app.AppDir Protodesk-${APP_VERSION}-${ARCH}.AppImage
