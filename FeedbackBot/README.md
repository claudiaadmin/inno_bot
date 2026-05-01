# Feedback Bot

A web app for collecting workshop feedback via voice recording or text input. Feedback is transcribed (via OpenAI Whisper), organized by day and group, and summarized using GPT-4o.

## Features

- Voice recording or typed text feedback
- Group selection (Anonymous, Group 1-5)
- Undo/redo submitted feedback
- Summaries organized by day of the week and group
- Day-of-week filtering on the summary page
- Cover page with voluntary participation notice

## Requirements

- Docker
- An OpenAI API key

## Quick Start (Docker)

1. Clone the repo and create a `.env` file:

```bash
git clone <your-repo-url>
cd FeedbackBot
nano .env
```

Add the following to `.env`:

```
OPENAI_API_KEY=sk-your-key
HOST="0.0.0.0"
PORT=8000
```

2. Build and run:

```bash
docker build -t feedbackbot .
docker run -d --name feedbackbot -p 8000:8000 -v $(pwd)/.env:/app/.env -v $(pwd)/data:/app/data feedbackbot
```

3. Open `http://your-machine-ip:8000` in a browser.

## Local Development (without Docker)

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/), and ffmpeg.

```bash
uv sync
uv run python -m feedbackbot.main
```

## HTTPS (optional)

For iOS devices (which require HTTPS for microphone access), generate self-signed certificates:

```bash
mkdir certificates
openssl req -x509 -newkey rsa:4096 -keyout certificates/key.pem -out certificates/cert.pem -days 365 -nodes
```

The app detects certificates automatically and enables HTTPS. For production, use certificates from Let's Encrypt or your provider.

## Useful Docker Commands

```bash
docker logs feedbackbot      # view logs
docker stop feedbackbot      # stop
docker start feedbackbot     # restart
docker rm feedbackbot        # remove
```
