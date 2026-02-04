from __future__ import annotations

from typing import Any, Dict, Optional


def create_tutorial(world: Dict[str, Any], skill_level: Optional[str]) -> Dict[str, Any]:
    return {
        "skill_level": skill_level or "adaptive",
        "steps": [
            "Movement and camera",
            "Combat basics",
            "Crafting and upgrades",
        ],
    }
