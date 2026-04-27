"""FastAPI entrypoint for the Resume Agent service."""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.agents.resume_agent import ResumeAgentError, analyze_resume_text
from backend.services.resume_parser import ResumeParsingError, parse_resume_file
from backend.services.settings_service import (
    SettingsError,
    get_openai_key_status,
    save_openai_api_key,
)

load_dotenv()

app = FastAPI(title="Resume Agent", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OpenAIKeyRequest(BaseModel):
    """Input model for local OpenAI key setup endpoint."""

    openai_api_key: str = Field(min_length=1)


class SettingsStatusResponse(BaseModel):
    """Output model for settings status endpoint."""

    openai_configured: bool
    key_status: Literal["configured", "missing", "invalid"]


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health endpoint for service monitoring."""

    status = "ok" if os.getenv("OPENAI_API_KEY") else "degraded"
    return {"status": status}


@app.get("/settings/status", response_model=SettingsStatusResponse)
def get_settings_status() -> SettingsStatusResponse:
    """Get OpenAI key configuration status for local development setup UI."""

    key_status = get_openai_key_status()
    return SettingsStatusResponse(
        openai_configured=key_status == "configured",
        key_status=key_status,
    )


@app.post("/settings/openai-key")
def save_settings_openai_key(payload: OpenAIKeyRequest) -> dict[str, str]:
    """Save OpenAI API key to local .env for development use only."""

    try:
        save_openai_api_key(payload.openai_api_key)
    except SettingsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail="Unexpected settings save error.") from exc

    return {"status": "saved"}


@app.post("/resume/analyze")
async def analyze_resume(file: UploadFile = File(...)) -> dict:
    """Upload a resume file and return normalized candidate profile JSON."""

    try:
        content = await file.read()
        resume_text = parse_resume_file(file.filename or "", content)
    except ResumeParsingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail="Unexpected file processing error.") from exc

    try:
        profile = analyze_resume_text(resume_text)
    except ResumeAgentError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail="Unexpected model processing error.") from exc

    return profile.model_dump()
