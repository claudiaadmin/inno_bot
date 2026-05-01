FROM python:3.13-alpine

# Install ffmpeg (needed for audio conversion)
RUN apk add --no-cache ffmpeg

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY feedbackbot/ feedbackbot/

# Create data directories
RUN mkdir -p data/recordings data/transcriptions

# Expose the port
EXPOSE 8000

CMD ["python", "-m", "feedbackbot.main"]
