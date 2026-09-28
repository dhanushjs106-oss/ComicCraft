from pathlib import Path
from typing import Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Spacer

from app.config import get_settings


class PDFService:
    def __init__(self):
        self.settings = get_settings()
        self.output_dir = Path(self.settings["pdf_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(self, story: Dict[str, Any]) -> str:
        safe_title = (story.get("title", "comiccraft") or "comiccraft").replace(" ", "_").lower()
        file_name = f"{safe_title}_comic.pdf"
        output_path = self.output_dir / file_name

        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story_content = []

        story_content.append(Paragraph(f"<b>{story.get('title', 'ComicCraft')}</b>", styles["Title"]))
        story_content.append(Spacer(1, 18))
        story_content.append(Paragraph(f"<b>Summary:</b> {story.get('summary', '')}", styles["BodyText"]))
        story_content.append(Spacer(1, 18))

        panels = story.get("panels", [])
        for panel in panels:
            story_content.append(Paragraph(f"<b>Panel {panel.get('panel_number', '')}</b>", styles["Heading2"]))
            image_url = panel.get("image_url")
            if image_url:
                relative_path = image_url.lstrip("/")
                try:
                    image_path = Path(relative_path)
                    if image_path.exists():
                        story_content.append(RLImage(str(image_path), width=220, height=180))
                    else:
                        story_content.append(Paragraph("Image unavailable for this panel.", styles["BodyText"]))
                except Exception:
                    story_content.append(Paragraph("Image unavailable for this panel.", styles["BodyText"]))
            else:
                story_content.append(Paragraph("Image unavailable for this panel.", styles["BodyText"]))

            story_content.append(Spacer(1, 12))
            story_content.append(Paragraph(f"<b>Narration:</b> {panel.get('narration', '')}", styles["BodyText"]))
            story_content.append(Paragraph(f"<b>Dialogue:</b> {panel.get('dialogue', '')}", styles["BodyText"]))
            story_content.append(Spacer(1, 18))

        doc.build(story_content)
        return str(output_path)
