"""Vercel serverless entry point for the MWLC Meal Planner."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "source.zip"
EXTRACT_DIR = Path("/tmp/mwlc_meal_planner")
MARKER = EXTRACT_DIR / ".ready"

if not MARKER.exists():
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE) as bundle:
        bundle.extractall(EXTRACT_DIR)
    MARKER.touch()

sys.path.insert(0, str(EXTRACT_DIR))

from app.main import app  # noqa: E402

__all__ = ["app"]
