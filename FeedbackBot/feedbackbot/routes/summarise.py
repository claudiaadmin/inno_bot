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
"""Summarise the feedback text using OpenAI GPT-4o model."""

import json
import re
from pathlib import Path

import openai
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from pypugjs.ext.jinja import PyPugJSExtension
from starlette.requests import Request
from ulid import ULID

from feedbackbot import database
from feedbackbot.types import SummaryResult, TranscriptionResult

__all__ = ["summary_router"]

summary_router: APIRouter = APIRouter()

# Set up the Jinja2 environment and extend it with PyPugJS
pug_templates_dir: Path = Path(__file__).parent.parent / "templates"
templates: Jinja2Templates = Jinja2Templates(directory=str(pug_templates_dir))
templates.env.add_extension(PyPugJSExtension)

PROMPT: str = """Summarise all the feedback into a single summary containing a summary, keywords,
    and sentiment analysis of the feedback. The input will be provided as a dictionary
    ' of dictionaries with the following structure: {"ULID": {"text": "Feedback"}}.'
    The output should be a dictionary with the following structure:
    ' {"summary": "Summary of the feedback text", "keywords": ["Keyword1",'
    ' "Keyword2"], "sentiment": "Positive/Negative/Neutral"}.'
    Please take care to provide the correct format for the output as it needs to be
    " automatically processed by the system."""


@summary_router.get("/summarise/", response_model=SummaryResult)
async def summarise_feedback() -> SummaryResult:
    """Endpoint to transcribe an uploaded audio file to text using OpenAI Whisper.

    Returns
    -------
        SummaryResult: Summary of the feedback text.

    """
    try:
        transcriptions: dict[ULID, TranscriptionResult] = database.load_transcriptions()
        transcripts: dict[str, dict[str, str]] = {
            str(ulid): {"text": transcription.text}
            for ulid, transcription in transcriptions.items()
        }

        model_input: list[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(content=PROMPT, role="system"),
            ChatCompletionUserMessageParam(
                role="user",
                content=json.dumps(transcripts),
            ),
        ]

        # Send the audio file to OpenAI Whisper API for transcription
        response: ChatCompletion = openai.chat.completions.create(
            model="gpt-4o",
            messages=model_input,
            temperature=0.5,
        )

        # Extract the summary, keywords, and sentiment from the response
        json_pattern: str = r"\{(?:[^{}]*|\{[^{}]*\})*\}"

        # Extract the JSON object from the response
        if not response.choices or not response.choices[0].message.content:
            return SummaryResult(
                summary="",
                keywords=[],
                sentiment="",
            )
        summary_response: str = response.choices[0].message.content
        match: re.Match[str] | None = re.search(
            pattern=json_pattern,
            string=summary_response,
        )

        default_summary: SummaryResult = SummaryResult(
            summary="",
            keywords=[],
            sentiment="",
        )
        if not match:
            return default_summary

        summary: dict[str, str | list[str]] = json.loads(match.group(0))

        # Remove any extra keys from the summary and ensure the correct types
        for key in summary:
            if key not in default_summary.__dict__:
                del summary[key]
        for key, value in default_summary.__dict__.items():
            if key not in summary:
                summary[key] = value
            if not isinstance(summary[key], type(value)):
                summary[key] = value

        return SummaryResult(**summary)  # type: ignore[arg-type]

    except openai.OpenAIError as err:
        raise HTTPException(
            status_code=500,
            detail=f"Error with OpenAI Whisper: {err}",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=str(err),
        ) from err


@summary_router.get("/summary", response_class=HTMLResponse)
async def get_index(request: Request) -> HTMLResponse:
    """Serve the summary page for summarising the feedback text."""
    return templates.TemplateResponse("summary.pug", {"request": request})
