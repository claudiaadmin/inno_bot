# coding=utf-8
# --------------------------------------------------------------------------------
# Project: Feedback Bot
# Author: Claudia Dresselhaus
# Year: 2024
# --------------------------------------------------------------------------------
#
# This code was generated with the help of AI writing assistants
# including GitHub Copilot, ChatGPT, Bing Chat.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Main entry point for the FastAPI application."""

import os
from pathlib import Path

import openai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from feedbackbot.routes import index_router, summary_router, transcribe_router

feedback_bot: FastAPI = FastAPI()
load_dotenv()

# Ensure to set your OpenAI API key here or in environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Set up static file serving
static_files_dir: Path = Path(__file__).parent / "static"
feedback_bot.mount(
    "/static",
    StaticFiles(directory=str(static_files_dir)),
    name="static",
)

# Include the routes
feedback_bot.include_router(index_router)
feedback_bot.include_router(summary_router)
feedback_bot.include_router(transcribe_router)


def main() -> None:
    """Run the FastAPI application."""
    host: str = os.environ.get("HOST", "localhost")
    port: int = int(os.environ.get("PORT", 8000))
    certificates_dir: Path = Path(__file__).parent.parent / "certificates"
    uvicorn.run(
        feedback_bot,
        host=host,
        port=port,
        ssl_keyfile=str(certificates_dir / "key.pem"),
        ssl_certfile=str(certificates_dir / "cert.pem"),
    )


if __name__ == "__main__":
    main()
