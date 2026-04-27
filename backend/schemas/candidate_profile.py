"""Pydantic schemas for normalized candidate profile output."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    """A single work-experience entry in a candidate profile."""

    company: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    responsibilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    """Normalized candidate profile extracted from resume text."""

    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    estimated_years_experience: float = 0
    seniority_level: str = ""
    career_signals: List[str] = Field(default_factory=list)
    missing_info: List[str] = Field(default_factory=list)
