import json
import re
from typing import Any, Dict, List

from google import genai
from google.genai import types

from app.config import get_settings


class GeminiService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings["gemini_api_key"]
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None
        self.model_candidates = [
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
            "gemini-flash-latest",
            "gemini-flash-lite-latest",
            "gemini-3.6-flash",
            "gemini-3.7-flash",
            "gemini-3.8-flash",
        ]

    def _get_model_candidates(self) -> List[str]:
        if not self.client:
            return self.model_candidates

        try:
            discovered = []
            for model in self.client.models.list():
                name = getattr(model, "name", "")
                if not name:
                    continue
                normalized = name.replace("models/", "")
                lowered = normalized.lower()
                supported_actions = getattr(model, "supported_actions", []) or []
                if "generateContent" not in supported_actions:
                    continue
                if any(
                    excluded in lowered
                    for excluded in ("tts", "image", "audio", "transcribe", "live", "robotics", "computer-use", "customtools")
                ):
                    continue
                if "gemini" not in lowered or "flash" not in lowered:
                    continue
                if normalized not in discovered:
                    discovered.append(normalized)

            preferred = []
            for preferred_name in self.model_candidates:
                if preferred_name in discovered and preferred_name not in preferred:
                    preferred.append(preferred_name)
            for candidate in discovered:
                if candidate not in preferred:
                    preferred.append(candidate)
            if preferred:
                return preferred
        except Exception:
            pass

        return self.model_candidates

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client is not None)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        if not text:
            raise ValueError("Gemini returned an empty response.")

        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).strip()

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Gemini returned invalid JSON.") from exc

    def _normalize_story(self, story: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(story, dict):
            raise ValueError("Gemini response was not a valid object.")

        if "title" not in story or "summary" not in story or "panels" not in story:
            raise ValueError("Gemini response did not include all required story data.")

        panel_count = int(request.get("panel_count", 4))
        panels = story.get("panels", [])
        if not isinstance(panels, list) or len(panels) == 0:
            raise ValueError("Gemini did not generate any comic panels.")

        normalized_panels: List[Dict[str, Any]] = []
        for index, panel in enumerate(panels[:panel_count], start=1):
            if not isinstance(panel, dict):
                continue
            normalized_panel = {
                "panel_number": int(panel.get("panel_number", index)),
                "description": str(panel.get("description", "")).strip(),
                "narration": str(panel.get("narration", "")).strip(),
                "dialogue": str(panel.get("dialogue", "")).strip(),
                "image_prompt": str(panel.get("image_prompt", "")).strip(),
            }
            normalized_panels.append(normalized_panel)

        if not normalized_panels:
            raise ValueError("Gemini did not produce valid panel content.")

        return {
            "title": str(story.get("title", "Untitled Comic")).strip() or "Untitled Comic",
            "summary": str(story.get("summary", "")).strip() or "A captivating comic story.",
            "panels": normalized_panels,
        }

    def generate_story(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("Gemini API key is missing or invalid.")

        prompt = self._build_prompt(request)
        last_error = None
        quota_error = None
        candidates = self._get_model_candidates()

        for model_name in candidates:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        response_mime_type="application/json",
                    ),
                )
                raw_text = getattr(response, "text", None)
                if not raw_text:
                    last_error = ValueError("Gemini returned no response content.")
                    continue
                story = self._extract_json(raw_text)
                return self._normalize_story(story, request)
            except Exception as exc:
                last_error = exc
                msg = str(exc).lower()
                if "quota" in msg or "rate limit" in msg or "429" in msg:
                    quota_error = exc
                    continue
                if "api key" in msg or "authentication" in msg or "forbidden" in msg:
                    raise ValueError("Unable to generate the story. Please check your Gemini API key or API quota.") from exc
                continue

        if quota_error is not None:
            raise ValueError(
                "Gemini API quota has been exceeded for the available Flash models. Please check your API quota or billing, then try again."
            ) from quota_error
        if last_error is not None:
            raise ValueError("Unable to generate the story. Gemini request failed.") from last_error
        raise ValueError("Unable to generate the story. Gemini request failed.")

    def _build_prompt(self, request: Dict[str, Any]) -> str:
        panel_count = request.get("panel_count", 4)
        story_prompt = request.get("story_prompt", "")
        character_name = request.get("character_name", "")
        setting = request.get("setting", "")
        tone = request.get("tone", "")
        art_style = request.get("art_style", "")

        return f"""
You are a professional comic book writer and creative director.
Write a coherent original comic story in valid JSON only.

Requirements:
- Title: a creative comic title.
- Summary: a short but vivid story overview.
- Panels: exactly {panel_count} unique panels, ordered from start to finish.
- Each panel must include:
  - panel_number: integer
  - description: concise scene description
  - narration: narration text
  - dialogue: quote or spoken dialogue for the panel
  - image_prompt: a detailed image-generation prompt that matches the panel's scene and the chosen art style

Use this story context:
- Story prompt: {story_prompt}
- Character name: {character_name}
- Setting: {setting}
- Tone: {tone}
- Art style: {art_style}

Return valid JSON with this structure:
{{
  "title": "...",
  "summary": "...",
  "panels": [
    {{
      "panel_number": 1,
      "description": "...",
      "narration": "...",
      "dialogue": "...",
      "image_prompt": "..."
    }}
  ]
}}

Important:
- Do not include markdown fences.
- Do not include any explanatory text outside the JSON.
- Ensure the image_prompt is rich enough for image generation and references the chosen art style.
- The story must feel complete and coherent.
"""
