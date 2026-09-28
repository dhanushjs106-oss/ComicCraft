import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def get_settings():
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    return {
        "gemini_api_key": gemini_key,
        "image_model": os.getenv("IMAGE_MODEL", "runwayml/stable-diffusion-v1-5"),
        "image_generation_enabled": os.getenv("IMAGE_GENERATION_ENABLED", "false").lower() in {"1", "true", "yes", "on"},
        "device": os.getenv("DEVICE", "auto"),
        "host": os.getenv("HOST", "127.0.0.1"),
        "port": int(os.getenv("PORT", "8000")),
        "base_dir": str(BASE_DIR),
        "generated_dir": str(BASE_DIR / "generated"),
        "image_dir": str(BASE_DIR / "generated" / "images"),
        "pdf_dir": str(BASE_DIR / "generated" / "pdf"),
    }
