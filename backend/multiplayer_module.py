from __future__ import annotations

from typing import Any, Dict, Optional


def configure_multiplayer(world: Dict[str, Any], mode: Optional[str]) -> Dict[str, Any]:
    return {
        "mode": mode or "co-op",
        "max_players": 4,
        "netcode": "lockstep_placeholder",
    }
