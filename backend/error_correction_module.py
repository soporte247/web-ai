from __future__ import annotations

from typing import Any, Dict, List


def validate_world(payload: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[str] = []
    if not payload.get("world"):
        issues.append("Missing world definition.")
    return {
        "issues": issues,
        "status": "ok" if not issues else "needs_review",
    }
