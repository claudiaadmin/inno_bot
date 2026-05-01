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
"""Data types for the application."""

from pydantic import BaseModel

__all__ = ["TranscriptionResult", "SummaryResult"]


class TranscriptionResult(BaseModel):
    """Response of Whisper Model."""

    text: str


class SummaryResult(BaseModel):
    """Response of ChatGPT (a Summary)."""

    summary: str
    keywords: list[str]
    sentiment: str
