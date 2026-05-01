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
"""Save audio and transcription data to the database."""

from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

import ffmpeg
from ulid import ULID

from feedbackbot.types import TranscriptionResult

# Constants for directory paths
DATA_DIR: Path = Path("data")
RECORDINGS_DIR: Path = DATA_DIR / "recordings"
TRANSCRIPTIONS_DIR: Path = DATA_DIR / "transcriptions"

# Ensure the directories exist
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)


def save_audio(
    audio_data: BytesIO,
    feedback_ulid: ULID,
) -> None:
    """Save an audio file to the database.

    Args:
    ----
        audio_data (BytesIO): The audio data in BytesIO format.
        feedback_ulid (ULID): The ULID of the feedback.

    """
    # Save the audio in a temporary file and then convert it to the desired format
    with NamedTemporaryFile("wb", suffix=".m4a", dir=RECORDINGS_DIR) as temp_file:
        audio_data.seek(0)
        temp_file.write(audio_data.getvalue())

        audio_path: Path = RECORDINGS_DIR / f"{feedback_ulid}.m4a"
        ffmpeg.input(temp_file.name).output(
            str(audio_path),
            format="ipod",
            acodec="aac",
            audio_bitrate="192k",
        ).run()


def save_transcription(
    transcription: TranscriptionResult,
    feedback_ulid: ULID,
) -> None:
    """Save a transcription to the database.

    Args:
    ----
        transcription (TranscriptionResult): The transcription data.
        feedback_ulid (ULID): The ULID of the feedback.

    """
    # Save the transcription file
    transcription_path: Path = TRANSCRIPTIONS_DIR / f"{feedback_ulid}.json"
    transcription_path.write_text(
        transcription.model_dump_json(indent=4),
        encoding="utf-8",
    )
