from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ComicPanel(BaseModel):
    panel_number: int = Field(..., ge=1)
    description: str = Field(..., min_length=1, max_length=2000)
    narration: str = Field(..., min_length=1, max_length=2000)
    dialogue: str = Field(..., min_length=1, max_length=2000)
    image_prompt: str = Field(..., min_length=1, max_length=3000)
    image_url: Optional[str] = None


class ComicStory(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    summary: str = Field(..., min_length=1, max_length=4000)
    panels: List[ComicPanel] = Field(..., min_items=1)


class StoryRequest(BaseModel):
    story_prompt: str = Field(..., min_length=10, max_length=1000)
    character_name: str = Field(..., min_length=1, max_length=100)
    setting: str = Field(..., min_length=1, max_length=200)
    tone: str = Field(..., min_length=1, max_length=50)
    art_style: str = Field(..., min_length=1, max_length=100)
    panel_count: int = Field(..., ge=3, le=8)

    @field_validator("story_prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def strip_and_validate_strings(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("This field must be a string.")
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class HealthResponse(BaseModel):
    status: str
    application: str
