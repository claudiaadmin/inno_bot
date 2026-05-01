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
from collections import defaultdict
from pathlib import Path

import openai
from fastapi import APIRouter, HTTPException, Query
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
from feedbackbot.types import DaySummary, GroupSummary, SummaryResult, TranscriptionResult

__all__ = ["summary_router"]

summary_router: APIRouter = APIRouter()

# Set up the Jinja2 environment and extend it with PyPugJS
pug_templates_dir: Path = Path(__file__).parent.parent / "templates"
templates: Jinja2Templates = Jinja2Templates(directory=str(pug_templates_dir))
templates.env.add_extension(PyPugJSExtension)

PROMPT: str = """Summarise the feedback organized by day and group. The input is structured as:
{"DayName": {"GroupName": ["feedback text 1", "feedback text 2"], ...}, ...}

Return a JSON object with this exact structure:
{"days": [{"day": "Monday", "groups": [{"group": "Group 1", "summary": "...", "keywords": ["k1", "k2"], "sentiment": "Positive/Negative/Neutral"}, ...]}, ...]}

For each group on each day, provide a summary of the feedback, relevant keywords, and overall sentiment.
If a day or group has no feedback, omit it. Ensure valid JSON output."""


@summary_router.get("/summarise/", response_model=SummaryResult)
async def summarise_feedback(
    day: str | None = Query(default=None),
) -> SummaryResult:
    """Summarise feedback grouped by day of the week and user group.

    Args:
    ----
        day: Optional day of the week filter (e.g. "Monday").

    Returns:
    -------
        SummaryResult: Per-day, per-group summary of the feedback.

    """
    try:
        transcriptions: dict[ULID, TranscriptionResult] = database.load_transcriptions()

        # Group transcriptions by day_of_week, then by username (group)
        grouped: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        for _ulid, t in transcriptions.items():
            if day and t.day_of_week != day:
                continue
            grouped[t.day_of_week][t.username].append(t.text)

        if not grouped:
            return SummaryResult(days=[])

        model_input: list[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(content=PROMPT, role="system"),
            ChatCompletionUserMessageParam(
                role="user",
                content=json.dumps(grouped),
            ),
        ]

        response: ChatCompletion = openai.chat.completions.create(
            model="gpt-4o",
            messages=model_input,
            temperature=0.5,
            response_format={"type": "json_object"},
        )

        if not response.choices or not response.choices[0].message.content:
            return SummaryResult(days=[])

        raw: dict = json.loads(response.choices[0].message.content)

        # Parse into structured models
        days: list[DaySummary] = []
        for day_data in raw.get("days", []):
            groups: list[GroupSummary] = []
            for group_data in day_data.get("groups", []):
                groups.append(
                    GroupSummary(
                        group=group_data.get("group", "Unknown"),
                        summary=group_data.get("summary", ""),
                        keywords=group_data.get("keywords", []),
                        sentiment=group_data.get("sentiment", ""),
                    ),
                )
            days.append(DaySummary(day=day_data.get("day", "Unknown"), groups=groups))

        return SummaryResult(days=days)

    except openai.OpenAIError as err:
        raise HTTPException(
            status_code=500,
            detail=f"Error with OpenAI: {err}",
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
