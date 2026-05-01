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
"""Landing page for the Feedback Bot web interface."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pypugjs.ext.jinja import PyPugJSExtension
from starlette.requests import Request

__all__ = ["index_router"]

index_router: APIRouter = APIRouter()

# Set up the Jinja2 environment and extend it with PyPugJS
pug_templates_dir: Path = Path(__file__).parent.parent / "templates"
templates: Jinja2Templates = Jinja2Templates(directory=str(pug_templates_dir))
templates.env.add_extension(PyPugJSExtension)


@index_router.get("/", response_class=HTMLResponse)
async def get_index(request: Request) -> HTMLResponse:
    """Serve the index page for recording audio and displaying the transcribed text."""
    return templates.TemplateResponse("index.pug", {"request": request})
