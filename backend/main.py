"""FastAPI entrypoint for the Resume Agent service."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile

from backend.agents.resume_agent import ResumeAgentError, analyze_resume_text
from backend.services.resume_parser import ResumeParsingError, parse_resume_file

load_dotenv()

app = FastAPI(title="Resume Agent", version="1.0.0")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health endpoint for service monitoring."""

    status = "ok" if os.getenv("OPENAI_API_KEY") else "degraded"
    return {"status": status}


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
