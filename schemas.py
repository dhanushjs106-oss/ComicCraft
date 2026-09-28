from typing import Optional

from pydantic import BaseModel, Field


class GenerateComicRequest(BaseModel):
    story_prompt: str = Field(..., min_length=10, max_length=1000)
    character_name: str = Field(..., min_length=1, max_length=100)
    setting: str = Field(..., min_length=1, max_length=200)
    tone: str = Field(..., min_length=1, max_length=50)
    art_style: str = Field(..., min_length=1, max_length=100)
    panel_count: int = Field(..., ge=3, le=8)


class PanelResponse(BaseModel):
    panel_number: int
    description: str
    narration: str
    dialogue: str
    image_prompt: str
    image_url: Optional[str] = None


class ComicResponse(BaseModel):
    title: str
    summary: str
    panels: list[PanelResponse]


class ErrorResponse(BaseModel):
    detail: str
