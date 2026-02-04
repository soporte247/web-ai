from __future__ import annotations

from typing import Any, Dict, Optional


def gather_context(prompt: str, theme: Optional[str] = None) -> Dict[str, Any]:
    focus = theme or "general"
    tags = [focus, "worldbuilding", "timeline"]
    return {
        "focus": focus,
        "tags": tags,
        "summary": "Research stub: replace with real historical or thematic retrieval.",
    }
