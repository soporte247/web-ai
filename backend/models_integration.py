from __future__ import annotations

import random
from typing import Any, Dict, List


def _pick_biomes(theme: str) -> List[str]:
    theme_lower = theme.lower()
    if "ciencia" in theme_lower or "futur" in theme_lower:
        return ["Neo City", "Industrial Dock", "Skyline", "Cyber District", "Tech Plaza"]
    if "fantas" in theme_lower:
        return ["Ancient Forest", "Crystal Ruins", "Sky Temple", "Mystic Lake", "Dragon Peak"]
    if "apocal" in theme_lower:
        return ["Desert Wastes", "Collapsed Metro", "Scrap Fields", "Toxic Swamp", "Bunker Complex"]
    if "terror" in theme_lower or "horror" in theme_lower:
        return ["Abandoned Hospital", "Dark Forest", "Haunted Manor", "Cemetery", "Underground Catacombs"]
    return ["City Center", "Outskirts", "Valley", "Mountain Pass", "River Delta"]


def _pick_missions(theme: str) -> List[Dict[str, Any]]:
    theme_lower = theme.lower()
    if "ciencia" in theme_lower or "futur" in theme_lower:
        return [
            {"name": "Signal Trace", "objective": "Locate the hidden transmitter", "difficulty": "easy", "rewards": ["Advanced Scanner", "100 Credits"]},
            {"name": "Data Heist", "objective": "Extract the security archive", "difficulty": "medium", "rewards": ["Encrypted Key", "250 Credits"]},
            {"name": "Overseer Finale", "objective": "Disable the central AI core", "difficulty": "hard", "rewards": ["AI Core Fragment", "1000 Credits"]},
            {"name": "Rescue Operation", "objective": "Save trapped scientists", "difficulty": "medium", "rewards": ["Science Kit", "300 Credits"]},
            {"name": "Prototype Theft", "objective": "Steal experimental weapon", "difficulty": "hard", "rewards": ["Plasma Rifle", "500 Credits"]},
        ]
    if "fantas" in theme_lower:
        return [
            {"name": "Crystal Pact", "objective": "Unite the shard guardians", "difficulty": "medium", "rewards": ["Crystal Shard", "Magic Staff"]},
            {"name": "Sky Relay", "objective": "Restore the floating sanctum", "difficulty": "hard", "rewards": ["Wings of Flight", "Ancient Tome"]},
            {"name": "Dragon Accord", "objective": "Negotiate with dragon lord", "difficulty": "hard", "rewards": ["Dragon Scale", "Fire Breath"]},
            {"name": "Forest Quest", "objective": "Cleanse corrupted spirits", "difficulty": "easy", "rewards": ["Nature Staff", "Health Potion"]},
            {"name": "Rune Search", "objective": "Find 5 ancient runes", "difficulty": "medium", "rewards": ["Rune Stone", "Teleport Scroll"]},
        ]
    if "apocal" in theme_lower:
        return [
            {"name": "Supply Run", "objective": "Find food and water", "difficulty": "easy", "rewards": ["Food Pack", "Water Filter"]},
            {"name": "Bunker Raid", "objective": "Clear infected bunker", "difficulty": "medium", "rewards": ["Gas Mask", "Shotgun"]},
            {"name": "Cure Research", "objective": "Collect samples for cure", "difficulty": "hard", "rewards": ["Antidote", "Medical Kit"]},
        ]
    return [
        {"name": "Prologue", "objective": "Discover the first clue", "difficulty": "easy", "rewards": ["Map", "Compass"]},
        {"name": "Crossing", "objective": "Reach the neutral territory", "difficulty": "medium", "rewards": ["Safe Pass", "Supplies"]},
        {"name": "Final Stand", "objective": "Resolve the main conflict", "difficulty": "hard", "rewards": ["Victory Medal", "Legendary Item"]},
    ]


def _generate_buildings(zone_type: str) -> List[Dict[str, Any]]:
    """Generate buildings based on zone type"""
    buildings = []
    if "city" in zone_type.lower() or "neo" in zone_type.lower():
        buildings = [
            {"type": "skyscraper", "height": random.randint(10, 30), "width": random.randint(4, 8), "depth": random.randint(4, 8), "color": "steel"},
            {"type": "tower", "height": random.randint(15, 25), "width": 3, "depth": 3, "color": "glass"},
            {"type": "plaza", "height": 2, "width": 10, "depth": 10, "color": "concrete"},
        ]
    elif "forest" in zone_type.lower():
        buildings = [
            {"type": "tree", "height": random.randint(8, 15), "width": 2, "depth": 2, "color": "green"},
            {"type": "ancient_stone", "height": 5, "width": 3, "depth": 3, "color": "stone"},
            {"type": "treehouse", "height": 10, "width": 4, "depth": 4, "color": "wood"},
        ]
    elif "temple" in zone_type.lower() or "ruin" in zone_type.lower():
        buildings = [
            {"type": "temple", "height": 12, "width": 8, "depth": 8, "color": "ancient"},
            {"type": "pillar", "height": 10, "width": 1, "depth": 1, "color": "marble"},
            {"type": "shrine", "height": 6, "width": 4, "depth": 4, "color": "gold"},
        ]
    else:
        buildings = [
            {"type": "house", "height": random.randint(3, 6), "width": random.randint(3, 5), "depth": random.randint(3, 5), "color": "brick"},
            {"type": "shop", "height": 4, "width": 5, "depth": 4, "color": "wood"},
        ]
    
    return buildings


def _generate_items(count: int = 10) -> List[Dict[str, Any]]:
    """Generate collectible items"""
    item_types = ["health_potion", "mana_potion", "coin", "gem", "key", "scroll", "weapon", "armor", "food", "tool"]
    items = []
    for i in range(count):
        items.append({
            "type": random.choice(item_types),
            "value": random.randint(10, 100),
            "rarity": random.choice(["common", "uncommon", "rare", "epic", "legendary"]),
            "position": {"x": random.uniform(-50, 50), "y": 1, "z": random.uniform(-50, 50)}
        })
    return items


def _generate_obstacles(count: int = 15) -> List[Dict[str, Any]]:
    """Generate obstacles and environmental objects"""
    obstacle_types = ["rock", "wall", "barrier", "crate", "barrel", "fence", "bush", "debris"]
    obstacles = []
    for i in range(count):
        obstacles.append({
            "type": random.choice(obstacle_types),
            "size": random.choice(["small", "medium", "large"]),
            "destructible": random.choice([True, False]),
            "position": {"x": random.uniform(-60, 60), "y": 0, "z": random.uniform(-60, 60)}
        })
    return obstacles


def generate_world(
    prompt: str,
    research_context: Dict[str, Any],
    platforms: List[str],
    enable_ar_vr: bool,
) -> Dict[str, Any]:
    summary = f"{prompt.strip().capitalize()}"
    theme = research_context.get("focus") or "general"
    biomes = _pick_biomes(theme)
    missions = _pick_missions(theme)

    # Generate rich zones with buildings
    zones = []
    for i, biome in enumerate(biomes[:5]):  # Up to 5 zones
        threat_level = ["low", "low", "medium", "high", "extreme"][i] if i < 5 else "high"
        zones.append({
            "name": biome,
            "threat": threat_level,
            "landmark": f"Zone {i+1} Landmark",
            "buildings": _generate_buildings(biome),
            "environment": {
                "weather": random.choice(["clear", "rainy", "foggy", "stormy", "snowy"]),
                "temperature": random.randint(-10, 40),
                "time": random.choice(["dawn", "day", "dusk", "night"])
            }
        })

    # Generate enhanced NPCs with more attributes
    npcs = [
        {
            "name": "Kai",
            "role": "Guide",
            "level": random.randint(5, 10),
            "health": random.randint(80, 120),
            "memory": ["Player is new", "Knows the city layout"],
            "behavior": "Adaptive support",
            "dialogue": ["Welcome, traveler!", "I can show you around.", "Stay safe out there."],
            "quests": ["Tutorial Quest", "City Tour"],
            "skills": ["Navigation", "Combat Training"]
        },
        {
            "name": "Nyx",
            "role": "Merchant",
            "level": random.randint(3, 8),
            "health": 100,
            "memory": ["Tracks player reputation"],
            "behavior": "Trades and reacts to alliances",
            "dialogue": ["Got some rare items!", "What are you buying?", "Come back anytime."],
            "inventory": ["Sword", "Shield", "Potion x5"],
            "prices": {"weapon": 150, "armor": 200, "potion": 20}
        },
        {
            "name": "Rex",
            "role": "Warrior",
            "level": random.randint(10, 15),
            "health": random.randint(150, 200),
            "memory": ["Veteran fighter"],
            "behavior": "Aggressive defender",
            "dialogue": ["I'll fight by your side!", "No enemy stands a chance!"],
            "skills": ["Heavy Attack", "Shield Bash", "War Cry"]
        },
        {
            "name": "Luna",
            "role": "Healer",
            "level": random.randint(8, 12),
            "health": random.randint(70, 100),
            "memory": ["Compassionate medic"],
            "behavior": "Support and heal",
            "dialogue": ["Let me heal you.", "Stay strong!", "I'm here to help."],
            "skills": ["Heal", "Cure", "Revive"]
        }
    ]

    # Generate diverse enemies
    enemies = [
        {"type": "Sentinel Drone", "behavior": "Patrol and alert", "tier": 1, "health": 50, "damage": 10, "speed": "fast", "ai": "patrol"},
        {"type": "Hunter Unit", "behavior": "Ambush and pursue", "tier": 2, "health": 80, "damage": 20, "speed": "medium", "ai": "aggressive"},
        {"type": "Boss Titan", "behavior": "Area control", "tier": 3, "health": 300, "damage": 50, "speed": "slow", "ai": "strategic"},
        {"type": "Swarm", "behavior": "Group attack", "tier": 1, "health": 20, "damage": 5, "speed": "very fast", "ai": "swarm"},
        {"type": "Elite Guard", "behavior": "Defensive", "tier": 2, "health": 120, "damage": 30, "speed": "medium", "ai": "defensive"},
    ]

    # Generate items and obstacles
    items = _generate_items(15)
    obstacles = _generate_obstacles(20)

    # Enhanced props with interaction
    props = [
        {"name": "Relay Tower", "type": "structure", "interactable": True, "action": "activate"},
        {"name": "Energy Gate", "type": "interactive", "interactable": True, "action": "unlock"},
        {"name": "Supply Cache", "type": "loot", "interactable": True, "action": "open"},
        {"name": "Healing Fountain", "type": "utility", "interactable": True, "action": "heal"},
        {"name": "Teleport Portal", "type": "transport", "interactable": True, "action": "teleport"},
        {"name": "Save Point", "type": "checkpoint", "interactable": True, "action": "save"},
    ]

    return {
        "summary": summary,
        "platforms": platforms,
        "enable_ar_vr": enable_ar_vr,
        "research_tags": research_context.get("tags", []),
        "theme": theme,
        "zones": zones,
        "missions": missions,
        "levels": [
            {
                "name": "Prologue",
                "goal": "Introduce the core conflict and mechanics",
                "biomes": biomes,
                "recommended_level": 1,
                "estimated_time": "30 minutes"
            },
            {
                "name": "Chapter 1",
                "goal": "Explore the first major zone",
                "biomes": biomes[:2],
                "recommended_level": 5,
                "estimated_time": "1 hour"
            },
            {
                "name": "Chapter 2",
                "goal": "Face increasing challenges",
                "biomes": biomes[2:4],
                "recommended_level": 10,
                "estimated_time": "1.5 hours"
            },
            {
                "name": "Finale",
                "goal": "Confront the final challenge",
                "biomes": [biomes[-1]],
                "recommended_level": 15,
                "estimated_time": "2 hours"
            }
        ],
        "npcs": npcs,
        "enemies": enemies,
        "props": props,
        "items": items,
        "obstacles": obstacles,
        "player": {
            "starting_level": 1,
            "starting_health": 100,
            "starting_mana": 50,
            "starting_inventory": ["Basic Sword", "Leather Armor", "Health Potion x3"],
            "starting_position": {"x": 0, "y": 2, "z": 0}
        },
        "game_mechanics": {
            "combat_system": "real-time" if enable_ar_vr else "turn-based",
            "difficulty": "adaptive",
            "save_system": "checkpoint",
            "multiplayer": "co-op",
            "progression": "experience-based"
        },
        "lighting": {
            "time_of_day": random.choice(["dawn", "day", "dusk", "night"]),
            "fog_density": random.uniform(0.01, 0.05),
            "color_grade": random.choice(["neon-cool", "warm-sunset", "cold-blue", "dramatic-red"]),
            "ambient": {"r": random.uniform(0.1, 0.3), "g": random.uniform(0.1, 0.3), "b": random.uniform(0.1, 0.3)},
            "directional": {"intensity": random.uniform(0.5, 1.5), "angle": random.randint(0, 360)}
        },
        "audio": {
            "bgm": f"{theme.lower()}_theme.mp3",
            "ambient": ["wind", "water", "crowd"] if "city" in theme.lower() else ["nature", "wildlife"],
            "combat": "battle_music.mp3"
        },
        "weather_system": {
            "enabled": True,
            "current": random.choice(["clear", "cloudy", "rainy", "stormy"]),
            "dynamic": True
        }
    }

