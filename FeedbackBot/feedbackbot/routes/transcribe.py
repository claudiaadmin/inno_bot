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
"""Transcribe audio files to text using OpenAI Whisper model."""

import io

import openai
from fastapi import APIRouter, Form, HTTPException, UploadFile
from pydantic import BaseModel
from openai.types.audio.transcription import Transcription
from ulid import ULID

from feedbackbot import database
from feedbackbot.types import TranscriptionResult

__all__ = ["transcribe_router"]

transcribe_router: APIRouter = APIRouter()


@transcribe_router.post("/transcribe/", response_model=FeedbackResponse)
async def transcribe_audio(
    file: UploadFile,
    username: str = Form(default="Anonymous"),
) -> FeedbackResponse:
    """Endpoint to transcribe an uploaded audio file to text using OpenAI Whisper.

    Args:
    ----
        file (UploadFile): The audio file to transcribe.

    Returns:
    -------
        TranscriptionResult: The transcribed text.

    """
    try:
        # Read the file content asynchronously
        audio_data: bytes = await file.read()

        # OpenAI Whisper expects a byte stream of the audio file
        audio_bytes: io.BytesIO = io.BytesIO(audio_data)
        audio_bytes.name = file.filename  # Set the name attribute

        feedback_ulid: ULID = ULID()
        try:
            database.save_audio(audio_data=audio_bytes, feedback_ulid=feedback_ulid)
        except Exception:  # noqa: BLE001
            print("Audio file could not be saved to the database.")

        # Send the audio file to OpenAI Whisper API for transcription
        audio_bytes.seek(0)  # Move the cursor to the beginning of the file
        transcription: Transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_bytes,
        )

        # Save the audio and transcription data to the database
        result = TranscriptionResult(text=transcription.text, username=username)
        database.save_transcription(
            transcription=result,
            feedback_ulid=feedback_ulid,
        )

        return FeedbackResponse(
            id=str(feedback_ulid),
            text=result.text,
            username=result.username,
        )

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


class FeedbackResponse(BaseModel):
    """Response with feedback text and its ID for undo support."""

    id: str
    text: str
    username: str


class TextFeedbackRequest(BaseModel):
    """Request body for typed text feedback."""

    text: str
    username: str = "Anonymous"


@transcribe_router.post("/feedback/", response_model=FeedbackResponse)
async def submit_text_feedback(body: TextFeedbackRequest) -> FeedbackResponse:
    """Endpoint to submit typed text feedback directly (no audio).

    Args:
    ----
        body: The text feedback and username.

    Returns:
    -------
        FeedbackResponse: The saved feedback with its ID.

    """
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Feedback text cannot be empty.")

    feedback_ulid: ULID = ULID()
    result = TranscriptionResult(text=body.text.strip(), username=body.username)
    database.save_transcription(
        transcription=result,
        feedback_ulid=feedback_ulid,
    )
    return FeedbackResponse(
        id=str(feedback_ulid),
        text=result.text,
        username=result.username,
    )


@transcribe_router.delete("/feedback/{feedback_id}")
async def delete_feedback(feedback_id: str) -> dict[str, bool]:
    """Delete a feedback entry by its ULID.

    Args:
    ----
        feedback_id: The ULID string of the feedback to delete.

    Returns:
    -------
        dict indicating success.

    """
    try:
        ulid = ULID.from_str(feedback_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="Invalid feedback ID.") from err

    deleted = database.delete_feedback(ulid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    return {"deleted": True}
