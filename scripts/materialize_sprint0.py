from __future__ import annotations

import base64
import hashlib
import shutil
import tarfile
from pathlib import Path

EXPECTED_SHA256 = "8dc512007b3865feb565eb8b30663e608bdc22802ff394842d52976326849eba"
ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "artifacts" / "sprint0_parts"
ARCHIVE = ROOT / "artifacts" / "mwlc_sprint0_source.tar.xz"


def main() -> None:
    encoded = b"".join(path.read_bytes().strip() for path in sorted(PARTS.glob("part*")))
    payload = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"Checksum mismatch: expected {EXPECTED_SHA256}, got {digest}")

    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_bytes(payload)
    with tarfile.open(ARCHIVE, "r:xz") as package:
        package.extractall(ROOT)

    print(f"Materialised Sprint 0 source from {len(list(PARTS.glob('part*')))} verified chunks.")
    print(f"SHA-256: {digest}")
    print("Next: pip install -r requirements.txt && pytest -q")


if __name__ == "__main__":
    main()
