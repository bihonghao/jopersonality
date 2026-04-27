"""Helpers for local development settings management."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import dotenv_values
from openai import OpenAI

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = ROOT_DIR / ".env"

KeyStatus = Literal["configured", "missing", "invalid"]


class SettingsError(Exception):
    """Raised when local settings persistence fails."""


def get_openai_api_key() -> str | None:
    """Return OPENAI_API_KEY from environment (dotenv-loaded or system env)."""

    key = os.getenv("OPENAI_API_KEY", "").strip()
    return key or None


def _validate_key_format(api_key: str) -> bool:
    return api_key.startswith("sk-") and len(api_key) >= 20


def _check_key_with_openai(api_key: str) -> bool:
    """Best-effort validity check using OpenAI models API."""

    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def get_openai_key_status() -> KeyStatus:
    """Return configuration state for OpenAI key."""

    api_key = get_openai_api_key()
    if not api_key:
        return "missing"

    if not _validate_key_format(api_key):
        return "invalid"

    if not _check_key_with_openai(api_key):
        return "invalid"

    return "configured"


def save_openai_api_key(api_key: str) -> None:
    """Persist OPENAI_API_KEY to local .env and current process environment."""

    normalized = api_key.strip()
    if not normalized:
        raise SettingsError("API key cannot be empty.")

    if not _validate_key_format(normalized):
        raise SettingsError("API key format is invalid.")

    if not _check_key_with_openai(normalized):
        raise SettingsError("API key is invalid or unauthorized.")

    existing_values = dotenv_values(ENV_FILE_PATH)
    existing_values["OPENAI_API_KEY"] = normalized

    try:
        lines = [f"{key}={value}" for key, value in existing_values.items() if value is not None]
        ENV_FILE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception as exc:  # pylint: disable=broad-except
        raise SettingsError("Unable to persist OPENAI_API_KEY to .env.") from exc

    os.environ["OPENAI_API_KEY"] = normalized
