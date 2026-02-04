from __future__ import annotations

from typing import Any, Dict, List


def optimize_physics(world: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
    return {
        "solver": "adaptive",
        "collision_profile": "auto",
        "platforms": platforms,
    }
