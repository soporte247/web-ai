from __future__ import annotations

import re
from datetime import datetime


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def safe_slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "world"
