from __future__ import annotations

from typing import Any, Dict, List


def generate_mods(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "name": "Hardcore Mode",
            "description": "Tighter resources and smarter enemies.",
        }
    ]
