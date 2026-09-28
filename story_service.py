from __future__ import annotations

from typing import Any, Dict, List

from app.config import get_settings
from app.gemini_service import GeminiService
from app.image_service import ImageService
from app.pdf_service import PDFService
from app.utils import ensure_directory


class StoryService:
    def __init__(self):
        self.settings = get_settings()
        self.gemini_service = GeminiService()
        self.image_service = ImageService()
        self.image_generation_enabled = self.settings["image_generation_enabled"]
        self.pdf_service = PDFService()
        ensure_directory(self.settings["image_dir"])
        ensure_directory(self.settings["pdf_dir"])

    def generate_story(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        request = {
            "story_prompt": str(request_data.get("story_prompt", "")).strip(),
            "character_name": str(request_data.get("character_name", "")).strip(),
            "setting": str(request_data.get("setting", "")).strip(),
            "tone": str(request_data.get("tone", "")).strip(),
            "art_style": str(request_data.get("art_style", "")).strip(),
            "panel_count": int(request_data.get("panel_count", 4)),
        }

        if not request["story_prompt"] or not request["character_name"] or not request["setting"]:
            raise ValueError("Please complete all story fields before generating the comic.")

        story = self.gemini_service.generate_story(request)

        generated_panels: List[Dict[str, Any]] = []
        for panel in story.get("panels", []):
            panel_number = int(panel.get("panel_number", len(generated_panels) + 1))
            image_url = None
            if self.image_generation_enabled and self.image_service.is_available():
                try:
                    image_url = self.image_service.generate_panel_image(panel, panel_number)
                except Exception:
                    image_url = None
            generated_panels.append(
                {
                    "panel_number": panel_number,
                    "description": panel.get("description", ""),
                    "narration": panel.get("narration", ""),
                    "dialogue": panel.get("dialogue", ""),
                    "image_prompt": panel.get("image_prompt", ""),
                    "image_url": image_url,
                }
            )

        final_story = {
            "title": story.get("title", "Untitled Comic"),
            "summary": story.get("summary", ""),
            "panels": generated_panels,
        }

        return final_story

    def generate_pdf(self, story: Dict[str, Any]) -> Dict[str, Any]:
        pdf_path = self.pdf_service.generate_pdf(story)
        file_name = pdf_path.split("/")[-1]
        return {"pdf_path": pdf_path, "pdf_url": f"/generated/pdf/{file_name}", "filename": file_name}
