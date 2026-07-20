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

# Patch the compact recipe-page macro cards without changing the larger
# dashboard cards used elsewhere in the guide.
import app.pdf_generator as pdf_generator  # noqa: E402

_original_metric_card = pdf_generator.metric_card


def _metric_card(c, x, y, w, h, value, label, fill=pdf_generator.PALE_BLUE):
    if h > 50:
        return _original_metric_card(c, x, y, w, h, value, label, fill)

    pdf_generator.rounded_box(c, x, y, w, h, fill, 10)
    centre = x + w / 2

    # Large value occupies the upper zone.
    c.setFillColor(pdf_generator.INK)
    c.setFont("Helvetica-Bold", 13.5)
    c.drawCentredString(centre, y + 25.5, pdf_generator._clean(value))

    # A quiet rule creates a clear visual break between value and label.
    c.setStrokeColor(pdf_generator.Color(0.82, 0.86, 0.91))
    c.setLineWidth(0.35)
    c.line(x + 12, y + 18, x + w - 12, y + 18)

    # Label sits in its own lower zone, away from the value.
    c.setFillColor(pdf_generator.MID)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawCentredString(centre, y + 7.5, pdf_generator._clean(label).upper())


pdf_generator.metric_card = _metric_card

from app.main import app  # noqa: E402

__all__ = ["app"]
