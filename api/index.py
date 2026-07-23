"""Vercel serverless entry point for the MWLC Meal Planner Sprint 1 release."""
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
SPRINT0_PARTS_DIR = REPOSITORY_ROOT / "artifacts" / "sprint0_parts"
SPRINT1_PARTS_DIR = REPOSITORY_ROOT / "artifacts" / "sprint1_parts"
EXTRACT_DIR = Path("/tmp/mwlc_meal_planner_sprint1")
MARKER = EXTRACT_DIR / ".ready"
SPRINT0_SHA256 = "8dc512007b3865feb565eb8b30663e608bdc22802ff394842d52976326849eba"
SPRINT1_SHA256 = "4b1ca9f3b9f2b48753a0d4d039ac9878d4712309159fcc89541973a4df8f04ef"
RELEASE_MARKER = f"{SPRINT0_SHA256}:{SPRINT1_SHA256}"


def _decode_overlay(parts_dir: Path, expected_sha256: str) -> bytes:
    encoded = b"".join(path.read_bytes().strip() for path in sorted(parts_dir.glob("part*")))
    payload = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256:
        raise RuntimeError(
            f"Overlay checksum mismatch for {parts_dir.name}: expected {expected_sha256}, got {digest}"
        )
    return payload


def _extract_overlay(payload: bytes) -> None:
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:xz") as package:
        package.extractall(EXTRACT_DIR)


def _prepare_application() -> None:
    if MARKER.exists() and MARKER.read_text(encoding="utf-8").strip() == RELEASE_MARKER:
        return

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    # Retain the existing licensed demonstration photography and brand assets.
    with zipfile.ZipFile(BASE_ARCHIVE) as bundle:
        bundle.extractall(EXTRACT_DIR)

    # Apply the reviewed Sprint 0 clinical and questionnaire release first.
    _extract_overlay(_decode_overlay(SPRINT0_PARTS_DIR, SPRINT0_SHA256))

    # Apply Sprint 1 data transfer, phenotype-informed selection and expanded recipes.
    _extract_overlay(_decode_overlay(SPRINT1_PARTS_DIR, SPRINT1_SHA256))

    MARKER.write_text(RELEASE_MARKER, encoding="utf-8")


_prepare_application()
sys.path.insert(0, str(EXTRACT_DIR))

from app.main import app  # noqa: E402

__all__ = ["app"]
