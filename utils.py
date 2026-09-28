import re
from pathlib import Path


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 _.-]", "", name).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or "comic"


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
