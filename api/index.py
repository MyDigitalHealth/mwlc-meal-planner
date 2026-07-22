"""Vercel serverless entry point for the MWLC Meal Planner Sprint 0 release."""
from __future__ import annotations

import base64
import hashlib
import io
import sys
import tarfile
import zipfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
BASE_ARCHIVE = REPOSITORY_ROOT / "source.zip"
PARTS_DIR = REPOSITORY_ROOT / "artifacts" / "sprint0_parts"
EXTRACT_DIR = Path("/tmp/mwlc_meal_planner_sprint0")
MARKER = EXTRACT_DIR / ".ready"
EXPECTED_SHA256 = "8dc512007b3865feb565eb8b30663e608bdc22802ff394842d52976326849eba"


def _prepare_application() -> None:
    if MARKER.exists() and MARKER.read_text(encoding="utf-8").strip() == EXPECTED_SHA256:
        return

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    # Retain the existing licensed demonstration photography and brand assets.
    with zipfile.ZipFile(BASE_ARCHIVE) as bundle:
        bundle.extractall(EXTRACT_DIR)

    # Reconstruct and verify the reviewed Sprint 0 source overlay.
    encoded = b"".join(path.read_bytes().strip() for path in sorted(PARTS_DIR.glob("part*")))
    payload = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f"Sprint 0 checksum mismatch: expected {EXPECTED_SHA256}, got {digest}")

    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:xz") as package:
        package.extractall(EXTRACT_DIR)

    MARKER.write_text(digest, encoding="utf-8")


_prepare_application()
sys.path.insert(0, str(EXTRACT_DIR))

from app.main import app  # noqa: E402

__all__ = ["app"]
