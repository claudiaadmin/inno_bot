FROM python:3.13-alpine

# Install ffmpeg (needed for audio conversion) and uv
RUN apk add --no-cache ffmpeg
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY feedbackbot/ feedbackbot/

# Create data directories
RUN mkdir -p data/recordings data/transcriptions

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "feedbackbot.main"]
