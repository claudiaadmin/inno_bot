FROM python:3.13-alpine

# Install ffmpeg (needed for audio conversion) and uv
RUN apk add --no-cache ffmpeg
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy everything needed for install
COPY pyproject.toml uv.lock README.md ./
COPY feedbackbot/ feedbackbot/

# Install dependencies (non-editable)
RUN uv sync --frozen --no-dev --no-editable

# Create data directories
RUN mkdir -p data/recordings data/transcriptions

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "feedbackbot.main"]
