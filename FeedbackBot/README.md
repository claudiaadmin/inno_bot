# Feedback Bot Application

## Installation
To install the project you will require Python 3.12 and uv.
To install simply run:

```bash
uv sync
```

You will also need to have ffmpeg installed to convert and save the audio files and openssl to generate certificates (The certificates are required to run the server in https as iOS will not allow audio recording on a unsecure page). These can be installed using a package manager like brew or apt-get.

To create the certificates, run:

```bash
mkdir certificates
openssl req -x509 -newkey rsa:4096 -keyout certificates/key.pem -out certificates/cert.pem -days 365 -nodes
```

## Running the application
To host the server you will need to know the IP address of the machine you are running the server on. This can be found by running:

```bash
ifconfig
```

The default port is 8000, but this can be changed in the config file. You may need to open the port on your router to allow external access.

To run the application, simply run:

```bash
poetry run feedbackbot
```
