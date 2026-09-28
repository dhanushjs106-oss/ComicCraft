from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.models import HealthResponse, StoryRequest
from app.story_service import StoryService

settings = get_settings()

app = FastAPI(
    title="ComicCraft",
    description="AI comic story creator using Gemini and diffusion models.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = Path(settings["base_dir"])
templates = Jinja2Templates(directory=str(base_dir / "templates"))
app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")
app.mount("/generated", StaticFiles(directory=str(base_dir / "generated")), name="generated")

story_service = StoryService()


@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> Dict[str, str]:
    return {"status": "healthy", "application": "ComicCraft"}


@app.post("/api/generate", tags=["Comic Generation"])
def generate_story(request: StoryRequest):
    try:
        result = story_service.generate_story(request.model_dump())
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        message = str(exc)
        if "Gemini" in message or "quota" in message.lower():
            raise HTTPException(status_code=500, detail="Unable to generate the story. Please check your Gemini API key or API quota.") from exc
        raise HTTPException(status_code=500, detail="Unable to generate the comic story. Please try again later.") from exc


@app.post("/api/generate-image", tags=["Image Generation"])
def generate_image(payload: Dict[str, Any]):
    try:
        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            raise ValueError("Image prompt is required.")
        image_url = story_service.image_service.generate_panel_image({"image_prompt": prompt}, 1)
        return {"image_url": image_url}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="The story was generated, but an illustration could not be created for this panel.")


@app.post("/api/download-pdf", tags=["PDF"])
def download_pdf(payload: Dict[str, Any]):
    try:
        if not payload:
            raise ValueError("Comic data is required.")
        result = story_service.generate_pdf(payload)
        pdf_path = result["pdf_path"]
        return FileResponse(path=pdf_path, filename=result["filename"], media_type="application/pdf")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="PDF generation failed. Please try again later.") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings["host"], port=settings["port"], reload=True)
