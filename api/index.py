"""Vercel serverless entry point for the MWLC Meal Planner Phase 2 review."""
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
PARTS_DIR = REPOSITORY_ROOT / "artifacts" / "phase2_parts"
EXTRACT_DIR = Path("/tmp/mwlc_meal_planner_phase2")
MARKER = EXTRACT_DIR / ".ready"
EXPECTED_SHA256 = "5bed8fa4790bd5732fff8e66dea3de51889c9e439b188a20adae55201e06987a"


def _prepare_application() -> None:
    if MARKER.exists() and MARKER.read_text(encoding="utf-8").strip() == EXPECTED_SHA256:
        return

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    # Preserve the existing licensed meal photography and brand assets.
    with zipfile.ZipFile(BASE_ARCHIVE) as bundle:
        bundle.extractall(EXTRACT_DIR)

    # Reconstruct and verify the reviewed Phase 2 source overlay.
    parts = sorted(PARTS_DIR.glob("part*"))
    if len(parts) != 8:
        raise RuntimeError(f"Expected 8 Phase 2 package parts, found {len(parts)}")

    encoded = b"".join(path.read_bytes().strip() for path in parts)
    payload = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f"Phase 2 checksum mismatch: expected {EXPECTED_SHA256}, got {digest}")

    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:xz") as package:
        package.extractall(EXTRACT_DIR)

    MARKER.write_text(digest, encoding="utf-8")


_prepare_application()
sys.path.insert(0, str(EXTRACT_DIR))

from app.main import app  # noqa: E402

__all__ = ["app"]
