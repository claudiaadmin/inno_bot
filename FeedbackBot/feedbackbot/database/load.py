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
"""Load transcription data to the database."""

import json
from pathlib import Path

from ulid import ULID

from feedbackbot.types import TranscriptionResult

# Constants for directory paths
DATA_DIR: Path = Path("data")
RECORDINGS_DIR: Path = DATA_DIR / "recordings"
TRANSCRIPTIONS_DIR: Path = DATA_DIR / "transcriptions"

__all__ = ["load_transcriptions"]


def load_transcriptions() -> dict[ULID, TranscriptionResult]:
    """Load transcription results from the database.

    Returns
    -------
        dict[ULID, TranscriptionResult]: A dictionary mapping record IDs to
        transcription results.

    """
    record_ids: list[ULID] = [
        ULID.from_str(record_transcript_file.stem)
        for record_transcript_file in TRANSCRIPTIONS_DIR.glob("*.json")
    ]

    transcriptions: dict[ULID, TranscriptionResult] = {}
    for record_id in record_ids:
        transcription_file: Path = TRANSCRIPTIONS_DIR / f"{record_id}.json"
        if not transcription_file.exists():
            continue
        with transcription_file.open("r") as file:
            record_json: dict[str, str] = json.load(file)
        result = TranscriptionResult(**record_json)

        # Derive timestamp and day_of_week from ULID for older records
        if not result.timestamp:
            ulid_dt = record_id.datetime
            result.timestamp = ulid_dt.isoformat()
            result.day_of_week = ulid_dt.strftime("%A")

        transcriptions[record_id] = result

    return transcriptions


