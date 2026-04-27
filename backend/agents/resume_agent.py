"""Agent responsible for converting resume text into structured candidate data."""

from __future__ import annotations

import json

from openai import OpenAI
from pydantic import ValidationError

from backend.schemas.candidate_profile import CandidateProfile
from backend.services.settings_service import get_openai_api_key


class ResumeAgentError(Exception):
    """Raised when the resume agent fails to produce valid output."""


def _build_prompt(resume_text: str) -> str:
    return (
        "Extract and normalize candidate profile information from the resume text below. "
        "Return ONLY valid JSON matching the exact schema fields and types. "
        "Use empty strings/arrays when data is missing.\n\n"
        f"Resume Text:\n{resume_text}"
    )


def analyze_resume_text(resume_text: str) -> CandidateProfile:
    """Use OpenAI to convert resume text into the normalized candidate profile schema."""

    api_key = get_openai_api_key()
    if not api_key:
        raise ResumeAgentError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    schema = CandidateProfile.model_json_schema()

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "candidate_profile",
                    "schema": schema,
                    "strict": True,
                },
            },
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise resume parsing assistant. "
                        "Always output valid JSON that follows the provided schema."
                    ),
                },
                {
                    "role": "user",
                    "content": _build_prompt(resume_text),
                },
            ],
        )
    except Exception as exc:  # pylint: disable=broad-except
        raise ResumeAgentError("Failed to get response from OpenAI.") from exc

    content = response.choices[0].message.content if response.choices else None
    if not content:
        raise ResumeAgentError("OpenAI returned an empty response.")

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ResumeAgentError("OpenAI response was not valid JSON.") from exc

    try:
        return CandidateProfile.model_validate(payload)
    except ValidationError as exc:
        raise ResumeAgentError("OpenAI JSON did not match candidate profile schema.") from exc
