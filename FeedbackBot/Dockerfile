FROM python:3.12-slim

# Install ffmpeg (needed for audio conversion)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

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
