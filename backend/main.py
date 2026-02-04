from __future__ import annotations

import json
import os
import sqlite3
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from openai import OpenAI

# import collaborative_story_module
# import error_correction_module
# import historical_research
# import learning_guide_module
# import models_integration
# import mods_module
# import multiplayer_module
# import physics_module
import simulation_module
from utils import now_iso, safe_slug
from local_ai import local_assistant

load_dotenv()

DEFAULT_DB_DIR = os.path.join(os.path.expanduser("~"), ".datashark")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "database.db")
DB_PATH = os.getenv("DATASHARK_DB_PATH", DEFAULT_DB_PATH)

app = FastAPI(title="DataShark AI Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[1]
# Remove problematic static mount - causes shutdown
# app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")


# Startup event
@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()


def _get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS worlds (
                id TEXT PRIMARY KEY,
                prompt TEXT NOT NULL,
                summary TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                user_id TEXT,
                is_public INTEGER DEFAULT 0,
                play_count INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0
            )
            """
        )
        columns = [row[1] for row in conn.execute("PRAGMA table_info(worlds)").fetchall()]
        if "user_id" not in columns:
            conn.execute("ALTER TABLE worlds ADD COLUMN user_id TEXT")
        if "is_public" not in columns:
            conn.execute("ALTER TABLE worlds ADD COLUMN is_public INTEGER DEFAULT 0")
        if "play_count" not in columns:
            conn.execute("ALTER TABLE worlds ADD COLUMN play_count INTEGER DEFAULT 0")
        if "likes" not in columns:
            conn.execute("ALTER TABLE worlds ADD COLUMN likes INTEGER DEFAULT 0")
        
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leaderboard (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                completed_missions INTEGER DEFAULT 0,
                play_time INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        
        # Game saves table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS game_saves (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                world_id TEXT NOT NULL,
                slot_name TEXT NOT NULL,
                slot_number INTEGER NOT NULL,
                game_state TEXT NOT NULL,
                player_stats TEXT NOT NULL,
                progress_percentage REAL DEFAULT 0.0,
                play_time INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (world_id) REFERENCES worlds(id),
                UNIQUE(user_id, world_id, slot_number)
            )
            """
        )
        
        # Achievements table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS achievements (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                icon TEXT,
                category TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                requirement TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        
        # User achievements table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_achievements (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (achievement_id) REFERENCES achievements(id),
                UNIQUE(user_id, achievement_id)
            )
            """
        )
        
        # Custom assets table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS custom_assets (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                asset_name TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                description TEXT,
                is_public INTEGER DEFAULT 0,
                downloads INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        
        # Player skills table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_skills (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                world_id TEXT NOT NULL,
                skill_tree TEXT NOT NULL,
                unlocked_skills TEXT NOT NULL,
                skill_points INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (world_id) REFERENCES worlds(id),
                UNIQUE(user_id, world_id)
            )
            """
        )
        
        # Quests table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quests (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                quest_type TEXT NOT NULL,
                requirements TEXT NOT NULL,
                rewards TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                branches TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id)
            )
            """
        )
        
        # User quests progress table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_quests (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                quest_id TEXT NOT NULL,
                status TEXT NOT NULL,
                progress TEXT NOT NULL,
                choices_made TEXT,
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (quest_id) REFERENCES quests(id),
                UNIQUE(user_id, quest_id)
            )
            """
        )
        
        # Crafting recipes table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS crafting_recipes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                result_item TEXT NOT NULL,
                result_quantity INTEGER DEFAULT 1,
                crafting_time INTEGER DEFAULT 0,
                required_level INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
            """
        )
        
        # Player inventory table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_inventory (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                world_id TEXT NOT NULL,
                items TEXT NOT NULL,
                currency INTEGER DEFAULT 0,
                capacity INTEGER DEFAULT 50,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (world_id) REFERENCES worlds(id),
                UNIQUE(user_id, world_id)
            )
            """
        )
        
        # Player reputation table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_reputation (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                world_id TEXT NOT NULL,
                faction_name TEXT NOT NULL,
                reputation_points INTEGER DEFAULT 0,
                rank TEXT DEFAULT 'neutral',
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (world_id) REFERENCES worlds(id),
                UNIQUE(user_id, world_id, faction_name)
            )
            """
        )
        
        # Player pets/companions table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_pets (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                world_id TEXT NOT NULL,
                pet_name TEXT NOT NULL,
                pet_type TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                stats TEXT NOT NULL,
                abilities TEXT NOT NULL,
                is_active INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (world_id) REFERENCES worlds(id)
            )
            """
        )
        
        # Player classes table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_classes (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                world_id TEXT NOT NULL,
                class_name TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                class_skills TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (world_id) REFERENCES worlds(id),
                UNIQUE(user_id, world_id)
            )
            """
        )
        
        # World events table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS world_events (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_name TEXT NOT NULL,
                description TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                event_data TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (world_id) REFERENCES worlds(id)
            )
            """
        )
        
        # Clans/guilds table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clans (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                leader_id TEXT NOT NULL,
                member_count INTEGER DEFAULT 1,
                clan_level INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (leader_id) REFERENCES users(id)
            )
            """
        )
        
        # Clan members table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clan_members (
                id TEXT PRIMARY KEY,
                clan_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                rank TEXT DEFAULT 'member',
                joined_at TEXT NOT NULL,
                FOREIGN KEY (clan_id) REFERENCES clans(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id)
            )
            """
        )
        
        # Player market listings table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_listings (
                id TEXT PRIMARY KEY,
                seller_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                item_name TEXT NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                description TEXT,
                is_sold INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (seller_id) REFERENCES users(id)
            )
            """
        )
        
        # Player statistics table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_stats (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                total_playtime INTEGER DEFAULT 0,
                enemies_defeated INTEGER DEFAULT 0,
                distance_traveled REAL DEFAULT 0.0,
                items_collected INTEGER DEFAULT 0,
                quests_completed INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                worlds_created INTEGER DEFAULT 0,
                achievements_unlocked INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id)
            )
            """
        )
        
        # User settings table (accessibility, graphics, audio)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                graphics_quality TEXT DEFAULT 'medium',
                audio_volume REAL DEFAULT 1.0,
                music_volume REAL DEFAULT 0.7,
                sfx_volume REAL DEFAULT 1.0,
                colorblind_mode TEXT DEFAULT 'none',
                subtitle_size TEXT DEFAULT 'medium',
                controls_config TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id)
            )
            """
        )
        
        # World templates table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS world_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                template_data TEXT NOT NULL,
                thumbnail_url TEXT,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        
        # Initialize default achievements
        default_achievements = [
            ("first_world", "First World Created", "Create your first world", "🌍", "creation", 10, "create_world:1"),
            ("world_master", "World Master", "Create 10 worlds", "🏆", "creation", 50, "create_world:10"),
            ("first_save", "First Steps", "Save your first game", "💾", "progress", 5, "save_game:1"),
            ("explorer", "Explorer", "Play 5 different worlds", "🗺️", "gameplay", 20, "play_world:5"),
            ("achievement_hunter", "Achievement Hunter", "Unlock 5 achievements", "🎯", "meta", 25, "unlock_achievement:5"),
            ("community_star", "Community Star", "Get 100 likes on your worlds", "⭐", "social", 100, "total_likes:100"),
            ("modder", "Modder", "Upload your first custom asset", "⚙️", "modding", 30, "upload_asset:1"),
            ("combat_master", "Combat Master", "Defeat 100 enemies", "⚔️", "combat", 40, "defeat_enemy:100"),
            ("collector", "Collector", "Collect 50 items", "💎", "gameplay", 15, "collect_item:50"),
            ("vr_pioneer", "VR Pioneer", "Play a world in VR mode", "🥽", "technology", 50, "play_vr:1"),
        ]
        
        for ach_id, name, desc, icon, category, points, requirement in default_achievements:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO achievements (id, name, description, icon, category, points, requirement, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (ach_id, name, desc, icon, category, points, requirement, now_iso())
                )
            except:
                pass
        
        # Initialize default crafting recipes
        default_recipes = [
            ("health_potion", "Health Potion", "Restores 50 HP", "consumable", 
             '{"herb":2,"water":1}', "health_potion", 1, 5, 1),
            ("iron_sword", "Iron Sword", "Basic melee weapon", "weapon",
             '{"iron_ore":3,"wood":1}', "iron_sword", 1, 30, 5),
            ("leather_armor", "Leather Armor", "Light armor", "armor",
             '{"leather":5,"thread":3}', "leather_armor", 1, 20, 3),
            ("mana_potion", "Mana Potion", "Restores 30 MP", "consumable",
             '{"crystal":1,"water":1}', "mana_potion", 1, 5, 1),
            ("steel_shield", "Steel Shield", "Heavy defense", "armor",
             '{"steel":4,"leather":2}', "steel_shield", 1, 45, 10),
        ]
        
        for recipe_id, name, desc, category, ingredients, result, qty, time, level in default_recipes:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO crafting_recipes 
                       (id, name, description, category, ingredients, result_item, result_quantity, crafting_time, required_level, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (recipe_id, name, desc, category, ingredients, result, qty, time, level, now_iso())
                )
            except:
                pass
        
        # Initialize default world templates
        default_templates = [
            ("dungeon_crawler", "Dungeon Crawler", "Classic dungeon with monsters and treasure", "dungeon",
             '{"biomes":["dark_cave","treasure_room","boss_chamber"],"difficulty":"medium"}'),
            ("open_world", "Open World Adventure", "Vast open world with multiple biomes", "exploration",
             '{"biomes":["forest","desert","mountains","ocean","city"],"difficulty":"easy"}'),
            ("survival_island", "Survival Island", "Stranded on a deserted island", "survival",
             '{"biomes":["beach","jungle","volcano"],"difficulty":"hard"}'),
            ("space_station", "Space Station", "Sci-fi space station exploration", "sci-fi",
             '{"biomes":["control_room","cargo_bay","reactor","airlock"],"difficulty":"medium"}'),
            ("fantasy_kingdom", "Fantasy Kingdom", "Medieval fantasy with castles and magic", "fantasy",
             '{"biomes":["castle","village","enchanted_forest","dragon_lair"],"difficulty":"medium"}'),
        ]
        
        for temp_id, name, desc, category, data in default_templates:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO world_templates 
                       (id, name, description, category, template_data, thumbnail_url, usage_count, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (temp_id, name, desc, category, data, None, 0, now_iso())
                )
            except:
                pass
        
        conn.commit()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
NPC_SYSTEM_PROMPT = os.getenv(
    "OPENAI_NPC_SYSTEM",
    "Eres un asistente NPC para creación de mundos. Responde breve, útil y en español."
    " Ayuda solo con el juego y la narrativa. Si te preguntan algo fuera del juego, redirige al contexto del juego."
)
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=5)
    theme: Optional[str] = None
    platforms: List[str] = Field(default_factory=lambda: ["Windows", "Mac", "Linux"])
    enable_ar_vr: bool = False
    multiplayer_mode: Optional[str] = None
    player_skill_level: Optional[str] = None
    user_id: Optional[str] = None


class GenerationResponse(BaseModel):
    world_id: str
    summary: str
    payload: Dict[str, Any]


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    id: str
    username: str
    token: str


class NpcChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: List[Dict[str, str]] = Field(default_factory=list)
    world_summary: Optional[str] = None


class NpcChatResponse(BaseModel):
    reply: str


class GameSaveRequest(BaseModel):
    world_id: str
    slot_name: str
    slot_number: int = Field(ge=1, le=10)
    game_state: Dict[str, Any]
    player_stats: Dict[str, Any]
    progress_percentage: float = Field(ge=0.0, le=100.0)
    play_time: int = Field(ge=0)


class GameSaveResponse(BaseModel):
    save_id: str
    message: str


class AchievementResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    category: str
    points: int
    unlocked: bool
    unlocked_at: Optional[str] = None


class CustomAssetUpload(BaseModel):
    asset_name: str
    asset_type: str
    file_data: str  # base64 encoded
    description: Optional[str] = None
    is_public: bool = False


class SkillTreeUpdate(BaseModel):
    world_id: str
    skill_id: str
    skill_tree: Dict[str, Any]


class AIProviderRequest(BaseModel):
    provider: str  # openai, claude, gemini, mistral
    message: str
    context: Optional[Dict[str, Any]] = None


# ========== NEW MODELS FOR ALL FEATURES ==========

class QuestCreate(BaseModel):
    world_id: str
    title: str
    description: str
    quest_type: str  # main, side, daily, weekly
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    difficulty: str  # easy, medium, hard
    branches: Optional[Dict[str, Any]] = None


class QuestProgress(BaseModel):
    quest_id: str
    status: str  # active, completed, failed
    progress: Dict[str, Any]
    choices_made: Optional[List[str]] = None


class QuestSeed(BaseModel):
    world_id: str


class CraftingRequest(BaseModel):
    recipe_id: str
    quantity: int = 1


class InventoryUpdate(BaseModel):
    world_id: str
    items: List[Dict[str, Any]]
    currency: int


class ReputationUpdate(BaseModel):
    world_id: str
    faction_name: str
    points_change: int


class PetCreate(BaseModel):
    world_id: str
    pet_name: str
    pet_type: str  # dog, cat, dragon, robot, etc
    stats: Dict[str, int]
    abilities: List[str]


class ClassSelect(BaseModel):
    world_id: str
    class_name: str  # warrior, mage, archer, rogue


class WorldEvent(BaseModel):
    world_id: str
    event_type: str  # meteor, invasion, festival, storm
    event_name: str
    description: str
    duration_minutes: int
    event_data: Dict[str, Any]


class ClanCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ClanInvite(BaseModel):
    clan_id: str
    user_id: str


class MarketListing(BaseModel):
    item_id: str
    item_name: str
    price: int
    quantity: int
    description: Optional[str] = None


class MarketPurchase(BaseModel):
    listing_id: str
    quantity: int


class SettingsUpdate(BaseModel):
    graphics_quality: Optional[str] = None
    audio_volume: Optional[float] = None
    music_volume: Optional[float] = None
    sfx_volume: Optional[float] = None
    colorblind_mode: Optional[str] = None
    subtitle_size: Optional[str] = None
    controls_config: Optional[Dict[str, Any]] = None


class TemplateCreate(BaseModel):
    name: str
    description: str
    category: str
    template_data: Dict[str, Any]
    thumbnail_url: Optional[str] = None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "timestamp": now_iso()}


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "name": "DataShark AI Backend",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "sample": "/sample",
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException) -> HTMLResponse:
        html = """
        <!doctype html>
        <html lang="es">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width,initial-scale=1" />
                <title>Error 404 - Página no encontrada</title>
                <style>
                    body {
                        margin: 0;
                        min-height: 100vh;
                        display: grid;
                        place-items: center;
                        background: #0b1020;
                        color: #e6e9f2;
                        font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
                    }
                    .wrap {
                        text-align: center;
                        padding: 24px;
                    }
                    h1 {
                        margin: 20px 0 8px;
                        font-size: 28px;
                    }
                    p {
                        margin: 0;
                        color: #a8b0c3;
                    }
                </style>
            </head>
            <body>
                <div class="wrap">
                    <h1>Error 404 - Página no encontrada</h1>
                    <p>La ruta solicitada no existe.</p>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=404)


@app.get("/favicon.ico")
def favicon() -> Response:
    return Response(status_code=204)


@app.get("/sample")
def sample_payload() -> Dict[str, Any]:
    example_request = GenerationRequest(
        prompt="Ciudad costera futurista con clima cambiante",
        theme="ciencia ficción",
        platforms=["Windows", "Mac", "Linux", "Android", "iOS"],
        enable_ar_vr=True,
        multiplayer_mode="co-op",
        player_skill_level="intermedio",
    ).model_dump()

    sample_research = historical_research.gather_context(
        example_request["prompt"], example_request["theme"]
    )
    sample_world = models_integration.generate_world(
        prompt=example_request["prompt"],
        research_context=sample_research,
        platforms=example_request["platforms"],
        enable_ar_vr=example_request["enable_ar_vr"],
    )
    sample_payload = {
        "world": sample_world,
        "research": sample_research,
        "simulations": simulation_module.simulate_systems(sample_world),
        "story": collaborative_story_module.build_story(sample_world),
        "tutorial": learning_guide_module.create_tutorial(sample_world, example_request["player_skill_level"]),
        "physics": physics_module.optimize_physics(sample_world, example_request["platforms"]),
        "multiplayer": multiplayer_module.configure_multiplayer(sample_world, example_request["multiplayer_mode"]),
    }

    return {
        "request": example_request,
        "response": {
            "world_id": safe_slug(sample_world["summary"]),
            "summary": sample_world["summary"],
            "payload": sample_payload,
        },
    }


@app.post("/generate", response_model=GenerationResponse)
def generate_world(request: GenerationRequest) -> GenerationResponse:
    research = historical_research.gather_context(request.prompt, request.theme)
    base_world = models_integration.generate_world(
        prompt=request.prompt,
        research_context=research,
        platforms=request.platforms,
        enable_ar_vr=request.enable_ar_vr,
    )
    simulations = simulation_module.simulate_systems(base_world)
    story = collaborative_story_module.build_story(base_world)
    tutorial = learning_guide_module.create_tutorial(base_world, request.player_skill_level)
    physics_profile = physics_module.optimize_physics(base_world, request.platforms)
    multiplayer = multiplayer_module.configure_multiplayer(base_world, request.multiplayer_mode)

    merged_payload: Dict[str, Any] = {
        "world": base_world,
        "research": research,
        "simulations": simulations,
        "story": story,
        "tutorial": tutorial,
        "physics": physics_profile,
        "multiplayer": multiplayer,
    }

    corrections = error_correction_module.validate_world(merged_payload)
    merged_payload["corrections"] = corrections
    merged_payload["mods"] = mods_module.generate_mods(merged_payload)

    summary = merged_payload["world"]["summary"]
    world_id = f"{safe_slug(summary)}-{uuid4().hex[:8]}"

    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO worlds (id, prompt, summary, payload, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (
                world_id,
                request.prompt,
                summary,
                json.dumps(merged_payload),
                now_iso(),
                request.user_id,
            ),
        )
        conn.commit()

    return GenerationResponse(world_id=world_id, summary=summary, payload=merged_payload)


@app.get("/worlds/{world_id}")
def get_world(world_id: str) -> Dict[str, Any]:
    with _get_connection() as conn:
        row = conn.execute("SELECT payload FROM worlds WHERE id = ?", (world_id,)).fetchone()

    if not row:
        return {"error": "World not found"}

    return json.loads(row["payload"])


@app.get("/worlds")
def list_worlds(user_id: Optional[str] = None) -> Dict[str, Any]:
    with _get_connection() as conn:
        if user_id:
            rows = conn.execute(
                "SELECT id, summary, created_at FROM worlds WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, summary, created_at FROM worlds ORDER BY created_at DESC LIMIT 20"
            ).fetchall()

    return {"worlds": [dict(row) for row in rows]}


@app.get("/worlds/{world_id}/export")
def export_world(world_id: str) -> Dict[str, Any]:
    with _get_connection() as conn:
        row = conn.execute("SELECT payload FROM worlds WHERE id = ?", (world_id,)).fetchone()

    if not row:
        return {"error": "World not found"}

    return {"format": "json", "payload": json.loads(row["payload"])}


@app.get("/worlds/{world_id}/versions")
def list_versions(world_id: str) -> Dict[str, Any]:
    return {
        "world_id": world_id,
        "versions": [
            {"id": f"{world_id}-v1", "label": "Initial", "created_at": now_iso()},
        ],
    }


@app.get("/mods")
def list_mods() -> Dict[str, Any]:
    return {
        "mods": [
            {"name": "Hardcore Mode", "description": "Tighter resources and smarter enemies."},
            {"name": "Explorer Mode", "description": "Low combat, high discovery."},
        ]
    }


@app.post("/lobby")
def lobby_create(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "room_id": f"room-{uuid4().hex[:6]}",
        "mode": payload.get("mode", "co-op"),
        "max_players": payload.get("max_players", 4),
    }


@app.get("/browse")
def browse_public_worlds(sort: str = "popular") -> Dict[str, Any]:
    """Browse public worlds created by other users"""
    with _get_connection() as conn:
        if sort == "popular":
            rows = conn.execute(
                """SELECT w.id, w.summary, w.created_at, w.play_count, w.likes, u.username 
                   FROM worlds w LEFT JOIN users u ON w.user_id = u.id 
                   WHERE w.is_public = 1 ORDER BY w.play_count DESC, w.likes DESC LIMIT 50"""
            ).fetchall()
        elif sort == "recent":
            rows = conn.execute(
                """SELECT w.id, w.summary, w.created_at, w.play_count, w.likes, u.username 
                   FROM worlds w LEFT JOIN users u ON w.user_id = u.id 
                   WHERE w.is_public = 1 ORDER BY w.created_at DESC LIMIT 50"""
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT w.id, w.summary, w.created_at, w.play_count, w.likes, u.username 
                   FROM worlds w LEFT JOIN users u ON w.user_id = u.id 
                   WHERE w.is_public = 1 ORDER BY w.likes DESC LIMIT 50"""
            ).fetchall()
    
    return {"worlds": [dict(row) for row in rows]}


@app.post("/worlds/{world_id}/publish")
def publish_world(world_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Make a world public so others can play it"""
    user_id = payload.get("user_id")
    
    with _get_connection() as conn:
        row = conn.execute("SELECT user_id FROM worlds WHERE id = ?", (world_id,)).fetchone()
        if not row:
            return {"error": "World not found"}
        
        if row["user_id"] != user_id:
            return {"error": "Unauthorized"}
        
        conn.execute("UPDATE worlds SET is_public = 1 WHERE id = ?", (world_id,))
        conn.commit()
    
    return {"success": True, "message": "World published successfully"}


@app.post("/worlds/{world_id}/unpublish")
def unpublish_world(world_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Make a world private"""
    user_id = payload.get("user_id")
    
    with _get_connection() as conn:
        row = conn.execute("SELECT user_id FROM worlds WHERE id = ?", (world_id,)).fetchone()
        if not row:
            return {"error": "World not found"}
        
        if row["user_id"] != user_id:
            return {"error": "Unauthorized"}
        
        conn.execute("UPDATE worlds SET is_public = 0 WHERE id = ?", (world_id,))
        conn.commit()
    
    return {"success": True, "message": "World unpublished"}


@app.post("/worlds/{world_id}/play")
def play_world(world_id: str) -> Dict[str, Any]:
    """Increment play count and return world data"""
    with _get_connection() as conn:
        conn.execute("UPDATE worlds SET play_count = play_count + 1 WHERE id = ?", (world_id,))
        conn.commit()
        
        row = conn.execute("SELECT payload, play_count FROM worlds WHERE id = ?", (world_id,)).fetchone()
        if not row:
            return {"error": "World not found"}
    
    return {"payload": json.loads(row["payload"]), "play_count": row["play_count"]}


@app.post("/worlds/{world_id}/like")
def like_world(world_id: str) -> Dict[str, Any]:
    """Like a world"""
    with _get_connection() as conn:
        conn.execute("UPDATE worlds SET likes = likes + 1 WHERE id = ?", (world_id,))
        conn.commit()
        
        row = conn.execute("SELECT likes FROM worlds WHERE id = ?", (world_id,)).fetchone()
        if not row:
            return {"error": "World not found"}
    
    return {"success": True, "likes": row["likes"]}


@app.get("/worlds/{world_id}/leaderboard")
def get_leaderboard(world_id: str) -> Dict[str, Any]:
    """Get leaderboard for a specific world"""
    with _get_connection() as conn:
        rows = conn.execute(
            """SELECT username, score, completed_missions, play_time, created_at 
               FROM leaderboard WHERE world_id = ? ORDER BY score DESC LIMIT 10""",
            (world_id,)
        ).fetchall()
    
    return {"leaderboard": [dict(row) for row in rows]}


@app.post("/worlds/{world_id}/leaderboard")
def submit_score(world_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Submit a score to the leaderboard"""
    user_id = payload.get("user_id")
    username = payload.get("username", "Anonymous")
    score = payload.get("score", 0)
    completed_missions = payload.get("completed_missions", 0)
    play_time = payload.get("play_time", 0)
    
    entry_id = f"{world_id}-{user_id}-{uuid4().hex[:8]}"
    
    with _get_connection() as conn:
        conn.execute(
            """INSERT INTO leaderboard (id, world_id, user_id, username, score, completed_missions, play_time, created_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (entry_id, world_id, user_id, username, score, completed_missions, play_time, now_iso())
        )
        conn.commit()
    
    return {"success": True, "entry_id": entry_id}


@app.post("/auth/register", response_model=AuthResponse)
def register(user: UserRegister) -> AuthResponse:
    import hashlib

    user_id = safe_slug(user.username)
    password_hash = hashlib.sha256(user.password.encode()).hexdigest()

    try:
        with _get_connection() as conn:
            conn.execute(
                "INSERT INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (user_id, user.username, password_hash, now_iso()),
            )
            conn.commit()
    except Exception:
        return AuthResponse(id=user_id, username=user.username, token="")

    token = f"{user_id}:{password_hash[:16]}"
    return AuthResponse(id=user_id, username=user.username, token=token)


@app.post("/auth/login", response_model=AuthResponse)
def login(user: UserLogin) -> AuthResponse:
    import hashlib

    password_hash = hashlib.sha256(user.password.encode()).hexdigest()

    with _get_connection() as conn:
        row = conn.execute(
            "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
            (user.username, password_hash),
        ).fetchone()

    if not row:
        return AuthResponse(id="", username="", token="")

    token = f"{row['id']}:{password_hash[:16]}"
    return AuthResponse(id=row["id"], username=row["username"], token=token)


# ============ GAME SAVES ENDPOINTS ============

@app.post("/saves/save", response_model=GameSaveResponse)
def save_game(save_data: GameSaveRequest, user_id: str) -> GameSaveResponse:
    """Save game progress for a specific world and slot"""
    save_id = str(uuid4())
    
    with _get_connection() as conn:
        # Check if save slot exists
        existing = conn.execute(
            "SELECT id FROM game_saves WHERE user_id = ? AND world_id = ? AND slot_number = ?",
            (user_id, save_data.world_id, save_data.slot_number)
        ).fetchone()
        
        if existing:
            # Update existing save
            conn.execute(
                """UPDATE game_saves SET 
                   slot_name = ?, game_state = ?, player_stats = ?, 
                   progress_percentage = ?, play_time = ?, updated_at = ?
                   WHERE id = ?""",
                (save_data.slot_name, json.dumps(save_data.game_state), 
                 json.dumps(save_data.player_stats), save_data.progress_percentage,
                 save_data.play_time, now_iso(), existing["id"])
            )
            save_id = existing["id"]
        else:
            # Create new save
            conn.execute(
                """INSERT INTO game_saves 
                   (id, user_id, world_id, slot_name, slot_number, game_state, player_stats, 
                    progress_percentage, play_time, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (save_id, user_id, save_data.world_id, save_data.slot_name, save_data.slot_number,
                 json.dumps(save_data.game_state), json.dumps(save_data.player_stats),
                 save_data.progress_percentage, save_data.play_time, now_iso(), now_iso())
            )
        conn.commit()
    
    return GameSaveResponse(save_id=save_id, message="Game saved successfully")


@app.get("/saves/list/{user_id}")
def list_saves(user_id: str) -> List[Dict[str, Any]]:
    """List all save slots for a user"""
    with _get_connection() as conn:
        rows = conn.execute(
            """SELECT gs.*, w.summary as world_name 
               FROM game_saves gs 
               LEFT JOIN worlds w ON gs.world_id = w.id
               WHERE gs.user_id = ? 
               ORDER BY gs.updated_at DESC""",
            (user_id,)
        ).fetchall()
    
    return [
        {
            "save_id": row["id"],
            "world_id": row["world_id"],
            "world_name": row["world_name"],
            "slot_name": row["slot_name"],
            "slot_number": row["slot_number"],
            "progress_percentage": row["progress_percentage"],
            "play_time": row["play_time"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
        for row in rows
    ]


@app.get("/saves/load/{save_id}")
def load_save(save_id: str) -> Dict[str, Any]:
    """Load a specific save"""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM game_saves WHERE id = ?",
            (save_id,)
        ).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Save not found")
    
    return {
        "save_id": row["id"],
        "world_id": row["world_id"],
        "slot_name": row["slot_name"],
        "slot_number": row["slot_number"],
        "game_state": json.loads(row["game_state"]),
        "player_stats": json.loads(row["player_stats"]),
        "progress_percentage": row["progress_percentage"],
        "play_time": row["play_time"],
        "updated_at": row["updated_at"]
    }


@app.delete("/saves/delete/{save_id}")
def delete_save(save_id: str, user_id: str) -> Dict[str, Any]:
    """Delete a save slot"""
    with _get_connection() as conn:
        conn.execute(
            "DELETE FROM game_saves WHERE id = ? AND user_id = ?",
            (save_id, user_id)
        )
        conn.commit()
    
    return {"success": True, "message": "Save deleted"}


# ============ ACHIEVEMENTS ENDPOINTS ============

@app.get("/achievements/list")
def list_achievements() -> List[Dict[str, Any]]:
    """List all available achievements"""
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM achievements ORDER BY category, points").fetchall()
    
    return [dict(row) for row in rows]


@app.get("/achievements/user/{user_id}")
def get_user_achievements(user_id: str) -> List[AchievementResponse]:
    """Get all achievements with unlock status for a user"""
    with _get_connection() as conn:
        rows = conn.execute(
            """SELECT a.*, ua.unlocked_at 
               FROM achievements a
               LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
               ORDER BY a.category, a.points""",
            (user_id,)
        ).fetchall()
    
    return [
        AchievementResponse(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            icon=row["icon"],
            category=row["category"],
            points=row["points"],
            unlocked=row["unlocked_at"] is not None,
            unlocked_at=row["unlocked_at"]
        )
        for row in rows
    ]


@app.post("/achievements/unlock/{user_id}/{achievement_id}")
def unlock_achievement(user_id: str, achievement_id: str) -> Dict[str, Any]:
    """Unlock an achievement for a user"""
    unlock_id = str(uuid4())
    
    try:
        with _get_connection() as conn:
            conn.execute(
                "INSERT INTO user_achievements (id, user_id, achievement_id, unlocked_at) VALUES (?, ?, ?, ?)",
                (unlock_id, user_id, achievement_id, now_iso())
            )
            conn.commit()
            
            # Get achievement details
            ach = conn.execute("SELECT * FROM achievements WHERE id = ?", (achievement_id,)).fetchone()
        
        return {
            "success": True,
            "achievement": dict(ach),
            "message": f"Achievement unlocked: {ach['name']}"
        }
    except:
        return {"success": False, "message": "Achievement already unlocked"}


@app.get("/achievements/progress/{user_id}")
def get_achievement_progress(user_id: str) -> Dict[str, Any]:
    """Get achievement progress statistics"""
    with _get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) as count FROM achievements").fetchone()["count"]
        unlocked = conn.execute(
            "SELECT COUNT(*) as count FROM user_achievements WHERE user_id = ?",
            (user_id,)
        ).fetchone()["count"]
        
        total_points = conn.execute("SELECT SUM(points) as total FROM achievements").fetchone()["total"]
        earned_points = conn.execute(
            """SELECT SUM(a.points) as total 
               FROM user_achievements ua 
               JOIN achievements a ON ua.achievement_id = a.id 
               WHERE ua.user_id = ?""",
            (user_id,)
        ).fetchone()["total"] or 0
    
    return {
        "total_achievements": total,
        "unlocked_achievements": unlocked,
        "completion_percentage": (unlocked / total * 100) if total > 0 else 0,
        "total_points": total_points,
        "earned_points": earned_points
    }


# ============ CUSTOM ASSETS ENDPOINTS ============

@app.post("/assets/upload")
def upload_custom_asset(asset: CustomAssetUpload, user_id: str) -> Dict[str, Any]:
    """Upload a custom 3D asset"""
    import base64
    
    asset_id = str(uuid4())
    assets_dir = os.path.join(os.path.dirname(DB_PATH), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Decode and save file
    file_extension = ".glb" if asset.asset_type == "model" else ".png"
    file_name = f"{asset_id}{file_extension}"
    file_path = os.path.join(assets_dir, file_name)
    
    try:
        file_bytes = base64.b64decode(asset.file_data)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        file_size = len(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save asset: {str(e)}")
    
    with _get_connection() as conn:
        conn.execute(
            """INSERT INTO custom_assets 
               (id, user_id, asset_name, asset_type, file_path, file_size, description, is_public, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (asset_id, user_id, asset.asset_name, asset.asset_type, file_path, 
             file_size, asset.description, 1 if asset.is_public else 0, now_iso())
        )
        conn.commit()
    
    return {
        "success": True,
        "asset_id": asset_id,
        "file_path": file_path,
        "message": "Asset uploaded successfully"
    }


@app.get("/assets/list/{user_id}")
def list_user_assets(user_id: str) -> List[Dict[str, Any]]:
    """List all assets uploaded by a user"""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM custom_assets WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
    
    return [dict(row) for row in rows]


@app.get("/assets/browse")
def browse_public_assets(asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Browse public assets"""
    with _get_connection() as conn:
        if asset_type:
            rows = conn.execute(
                "SELECT * FROM custom_assets WHERE is_public = 1 AND asset_type = ? ORDER BY downloads DESC, likes DESC",
                (asset_type,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM custom_assets WHERE is_public = 1 ORDER BY downloads DESC, likes DESC"
            ).fetchall()
    
    return [dict(row) for row in rows]


@app.post("/assets/{asset_id}/like")
def like_asset(asset_id: str) -> Dict[str, Any]:
    """Like a custom asset"""
    with _get_connection() as conn:
        conn.execute(
            "UPDATE custom_assets SET likes = likes + 1 WHERE id = ?",
            (asset_id,)
        )
        conn.commit()
    
    return {"success": True}


# ============ SKILL TREE ENDPOINTS ============

@app.post("/skills/update")
def update_skill_tree(skill_update: SkillTreeUpdate, user_id: str) -> Dict[str, Any]:
    """Update player skill tree"""
    skill_id = str(uuid4())
    
    with _get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM player_skills WHERE user_id = ? AND world_id = ?",
            (user_id, skill_update.world_id)
        ).fetchone()
        
        if existing:
            conn.execute(
                """UPDATE player_skills SET 
                   skill_tree = ?, unlocked_skills = ?, skill_points = ?, updated_at = ?
                   WHERE id = ?""",
                (json.dumps(skill_update.skill_tree), 
                 json.dumps([skill_update.skill_id]), 
                 0, now_iso(), existing["id"])
            )
        else:
            conn.execute(
                """INSERT INTO player_skills 
                   (id, user_id, world_id, skill_tree, unlocked_skills, skill_points, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (skill_id, user_id, skill_update.world_id, 
                 json.dumps(skill_update.skill_tree), json.dumps([skill_update.skill_id]), 
                 0, now_iso(), now_iso())
            )
        conn.commit()
    
    return {"success": True, "message": "Skill tree updated"}


@app.get("/skills/{user_id}/{world_id}")
def get_skill_tree(user_id: str, world_id: str) -> Dict[str, Any]:
    """Get player skill tree for a world"""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM player_skills WHERE user_id = ? AND world_id = ?",
            (user_id, world_id)
        ).fetchone()
    
    if not row:
        return {
            "skill_tree": {},
            "unlocked_skills": [],
            "skill_points": 0
        }
    
    return {
        "skill_tree": json.loads(row["skill_tree"]),
        "unlocked_skills": json.loads(row["unlocked_skills"]),
        "skill_points": row["skill_points"]
    }


# ============ MULTI AI PROVIDER ENDPOINT ============

@app.post("/ai/generate")
def generate_with_ai(request: AIProviderRequest) -> Dict[str, Any]:
    """Generate content using different AI providers"""
    
    if request.provider == "openai":
        if not openai_client:
            raise HTTPException(status_code=503, detail="OpenAI not configured")
        
        try:
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful game design assistant."},
                    {"role": "user", "content": request.message}
                ],
                max_tokens=500
            )
            return {
                "provider": "openai",
                "response": response.choices[0].message.content,
                "success": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    elif request.provider == "claude":
        # Anthropic Claude integration (requires anthropic package)
        return {
            "provider": "claude",
            "response": "Claude integration coming soon. Install: pip install anthropic",
            "success": False
        }
    
    elif request.provider == "gemini":
        # Google Gemini integration (requires google-generativeai package)
        return {
            "provider": "gemini",
            "response": "Gemini integration coming soon. Install: pip install google-generativeai",
            "success": False
        }
    
    elif request.provider == "mistral":
        # Mistral AI integration
        return {
            "provider": "mistral",
            "response": "Mistral integration coming soon. Install: pip install mistralai",
            "success": False
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported AI provider")


# ============ PHYSICS CONFIG ENDPOINT ============

@app.get("/physics/config")
def get_physics_config() -> Dict[str, Any]:
    """Get physics engine configuration"""
    return {
        "engine": "cannon.js",
        "gravity": -9.81,
        "timestep": 1/60,
        "iterations": 10,
        "collision_detection": "continuous",
        "features": {
            "destructible_objects": True,
            "ragdoll_physics": True,
            "vehicle_physics": True,
            "soft_bodies": False
        }
    }


# ============ ANIMATION PRESETS ENDPOINT ============

@app.get("/animations/presets")
def get_animation_presets() -> Dict[str, List[str]]:
    """Get available animation presets"""
    return {
        "character": ["idle", "walk", "run", "jump", "attack", "hit", "death"],
        "npc": ["idle", "talk", "wave", "sit", "work"],
        "enemy": ["idle", "patrol", "chase", "attack", "hurt", "death"],
        "transitions": ["idle_to_walk", "walk_to_run", "run_to_jump"]
    }


# ============ VR/AR CONFIG ENDPOINT ============

@app.get("/vr/config")
def get_vr_config() -> Dict[str, Any]:
    """Get VR/AR configuration"""
    return {
        "webxr_enabled": True,
        "supported_modes": ["immersive-vr", "immersive-ar"],
        "features": {
            "hand_tracking": True,
            "spatial_audio": True,
            "teleportation": True,
            "controllers": True
        },
        "settings": {
            "fov": 90,
            "ipd": 0.064,
            "render_scale": 1.0
        }
    }


@app.get("/combat/skills")
def get_combat_skills() -> Dict[str, Any]:
    """Get available combat skills and combos"""
    return {
        "basic_skills": [
            {"id": "light_attack", "name": "Light Attack", "damage": 10, "cooldown": 0.5},
            {"id": "heavy_attack", "name": "Heavy Attack", "damage": 25, "cooldown": 2.0},
            {"id": "block", "name": "Block", "reduction": 0.5, "cooldown": 0.0},
            {"id": "dodge", "name": "Dodge", "cooldown": 1.0}
        ],
        "combos": [
            {"name": "Quick Strike", "sequence": ["light_attack", "light_attack"], "bonus_damage": 5},
            {"name": "Power Slam", "sequence": ["heavy_attack", "light_attack"], "bonus_damage": 15},
            {"name": "Counter", "sequence": ["block", "heavy_attack"], "bonus_damage": 20}
        ],
        "skill_trees": {
            "warrior": ["strength", "endurance", "weapon_mastery"],
            "mage": ["intelligence", "mana", "spell_power"],
            "rogue": ["dexterity", "stealth", "critical_strike"]
        }
    }


# ============ GAME SAVES ENDPOINTS ============

@app.post("/saves/save", response_model=GameSaveResponse)
def save_game(save_data: GameSaveRequest, user_id: str) -> GameSaveResponse:
    """Save game progress for a specific world and slot"""
    save_id = str(uuid4())
    
    with _get_connection() as conn:
        # Check if save slot exists
        existing = conn.execute(
            "SELECT id FROM game_saves WHERE user_id = ? AND world_id = ? AND slot_number = ?",
            (user_id, save_data.world_id, save_data.slot_number)
        ).fetchone()
        
        if existing:
            # Update existing save
            conn.execute(
                """UPDATE game_saves SET 
                   slot_name = ?, game_state = ?, player_stats = ?, 
                   progress_percentage = ?, play_time = ?, updated_at = ?
                   WHERE id = ?""",
                (save_data.slot_name, json.dumps(save_data.game_state), 
                 json.dumps(save_data.player_stats), save_data.progress_percentage,
                 save_data.play_time, now_iso(), existing["id"])
            )
            save_id = existing["id"]
        else:
            # Create new save
            conn.execute(
                """INSERT INTO game_saves 
                   (id, user_id, world_id, slot_name, slot_number, game_state, player_stats, 
                    progress_percentage, play_time, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (save_id, user_id, save_data.world_id, save_data.slot_name, save_data.slot_number,
                 json.dumps(save_data.game_state), json.dumps(save_data.player_stats),
                 save_data.progress_percentage, save_data.play_time, now_iso(), now_iso())
            )
        conn.commit()
    
    return GameSaveResponse(save_id=save_id, message="Game saved successfully")


@app.post("/npc/chat", response_model=NpcChatResponse)
def npc_chat(payload: NpcChatRequest) -> NpcChatResponse:
    """Chat con asistente local (sin APIs externas)"""
    
    # Preparar contexto del mundo si está disponible
    context = {}
    if payload.world_summary:
        context["world_name"] = payload.world_summary
    
    # Obtener respuesta del asistente local
    reply = local_assistant.get_response(payload.message, context)
    
    return NpcChatResponse(reply=reply)


@app.get("/npc/tutorial/{topic}")
def get_tutorial(topic: str) -> Dict[str, str]:
    """Obtener tutorial específico"""
    tutorial_text = local_assistant.get_tutorial(topic)
    return {"topic": topic, "content": tutorial_text}


@app.get("/npc/faq")
def get_faq() -> Dict[str, Any]:
    """Obtener lista de preguntas frecuentes"""
    faqs = local_assistant.get_faq()
    return {"faqs": faqs, "total": len(faqs)}


# ============ QUESTS SYSTEM ENDPOINTS ============

@app.post("/quests/create")
def create_quest(quest: QuestCreate, user_id: str) -> Dict[str, Any]:
    """Create a new quest for a world"""
    quest_id = str(uuid4())
    
    with _get_connection() as conn:
        conn.execute(
            """INSERT INTO quests 
               (id, world_id, title, description, quest_type, requirements, rewards, difficulty, branches, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (quest_id, quest.world_id, quest.title, quest.description, quest.quest_type,
             json.dumps(quest.requirements), json.dumps(quest.rewards), quest.difficulty,
             json.dumps(quest.branches) if quest.branches else None, now_iso())
        )
        conn.commit()
    
    return {"quest_id": quest_id, "message": "Quest created successfully"}


@app.get("/quests/{world_id}")
def get_world_quests(world_id: str) -> Dict[str, Any]:
    """Get all quests for a world"""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM quests WHERE world_id = ?",
            (world_id,)
        ).fetchall()
        
        quests = []
        for row in rows:
            quests.append({
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "quest_type": row["quest_type"],
                "difficulty": row["difficulty"],
                "requirements": json.loads(row["requirements"]),
                "rewards": json.loads(row["rewards"]),
                "branches": json.loads(row["branches"]) if row["branches"] else None
            })
        
        return {"quests": quests, "total": len(quests)}


@app.post("/quests/progress")
def update_quest_progress(progress: QuestProgress, user_id: str) -> Dict[str, Any]:
    """Update user's quest progress"""
    progress_id = str(uuid4())
    
    with _get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM user_quests WHERE user_id = ? AND quest_id = ?",
            (user_id, progress.quest_id)
        ).fetchone()
        
        if existing:
            conn.execute(
                """UPDATE user_quests SET status = ?, progress = ?, choices_made = ?, completed_at = ?
                   WHERE id = ?""",
                (progress.status, json.dumps(progress.progress), 
                 json.dumps(progress.choices_made) if progress.choices_made else None,
                 now_iso() if progress.status == "completed" else None, existing["id"])
            )
        else:
            conn.execute(
                """INSERT INTO user_quests (id, user_id, quest_id, status, progress, choices_made, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (progress_id, user_id, progress.quest_id, progress.status, json.dumps(progress.progress),
                 json.dumps(progress.choices_made) if progress.choices_made else None,
                 now_iso() if progress.status == "completed" else None)
            )
        conn.commit()
    
    return {"message": "Quest progress updated"}


@app.post("/quests/seed")
def seed_quests(payload: QuestSeed) -> Dict[str, Any]:
    """Seed default quests for a world if none exist"""
    with _get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM quests WHERE world_id = ?",
            (payload.world_id,)
        ).fetchone()

        if existing:
            return {"message": "Quests already exist", "seeded": 0}

        defaults = [
            {
                "title": "Explora el primer bioma",
                "description": "Visita el bioma principal y habla con un NPC.",
                "quest_type": "main",
                "requirements": {"visit_biome": 1, "talk_npc": 1},
                "rewards": {"xp": 100, "coins": 50},
                "difficulty": "easy",
                "branches": {"choices": ["ayudar", "ignorar"]}
            },
            {
                "title": "Recolecta materiales",
                "description": "Recolecta 5 materiales comunes del entorno.",
                "quest_type": "side",
                "requirements": {"collect_items": 5},
                "rewards": {"xp": 80, "coins": 40},
                "difficulty": "easy",
                "branches": None
            },
            {
                "title": "Derrota enemigos",
                "description": "Derrota 3 enemigos del bioma actual.",
                "quest_type": "daily",
                "requirements": {"defeat_enemies": 3},
                "rewards": {"xp": 120, "coins": 70},
                "difficulty": "medium",
                "branches": None
            }
        ]

        for quest in defaults:
            conn.execute(
                """INSERT INTO quests 
                   (id, world_id, title, description, quest_type, requirements, rewards, difficulty, branches, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid4()),
                    payload.world_id,
                    quest["title"],
                    quest["description"],
                    quest["quest_type"],
                    json.dumps(quest["requirements"]),
                    json.dumps(quest["rewards"]),
                    quest["difficulty"],
                    json.dumps(quest["branches"]) if quest["branches"] else None,
                    now_iso(),
                )
            )
        conn.commit()

    return {"message": "Default quests seeded", "seeded": len(defaults)}


# ============ CRAFTING SYSTEM ENDPOINTS ============

@app.get("/crafting/recipes")
def get_crafting_recipes() -> Dict[str, Any]:
    """Get all crafting recipes"""
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM crafting_recipes").fetchall()
        
        recipes = []
        for row in rows:
            recipes.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "category": row["category"],
                "ingredients": json.loads(row["ingredients"]),
                "result_item": row["result_item"],
                "result_quantity": row["result_quantity"],
                "crafting_time": row["crafting_time"],
                "required_level": row["required_level"]
            })
        
        return {"recipes": recipes, "total": len(recipes)}


@app.post("/crafting/craft")
def craft_item(craft_request: CraftingRequest, user_id: str = Query(...)) -> Dict[str, Any]:
    """Craft an item from a recipe"""
    with _get_connection() as conn:
        recipe = conn.execute(
            "SELECT * FROM crafting_recipes WHERE id = ?",
            (craft_request.recipe_id,)
        ).fetchone()
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Add crafted item to inventory
        item_id = str(uuid4())
        quantity_crafted = recipe["result_quantity"] * craft_request.quantity
        
        conn.execute(
            """INSERT INTO player_inventory 
               (id, user_id, item_name, item_id, quantity, rarity, type, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (item_id, user_id, recipe["name"], recipe["result_item"], 
             quantity_crafted, "common", recipe["category"], now_iso())
        )
        conn.commit()
        
        return {
            "success": True,
            "crafted_item": recipe["result_item"],
            "quantity": quantity_crafted,
            "message": f"Crafted {recipe['name']} x{craft_request.quantity}"
        }


# ============ INVENTORY SYSTEM ENDPOINTS ============

@app.get("/inventory/{user_id}/{world_id}")
def get_inventory(user_id: str, world_id: str) -> Dict[str, Any]:
    """Get player's inventory"""
    with _get_connection() as conn:
        inventory = conn.execute(
            "SELECT * FROM player_inventory WHERE user_id = ? AND world_id = ?",
            (user_id, world_id)
        ).fetchone()
        
        if not inventory:
            return {"items": [], "currency": 0, "capacity": 50}
        
        return {
            "items": json.loads(inventory["items"]),
            "currency": inventory["currency"],
            "capacity": inventory["capacity"]
        }


@app.post("/inventory/update")
def update_inventory(inventory_data: InventoryUpdate, user_id: str) -> Dict[str, Any]:
    """Update player's inventory"""
    with _get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM player_inventory WHERE user_id = ? AND world_id = ?",
            (user_id, inventory_data.world_id)
        ).fetchone()
        
        if existing:
            conn.execute(
                "UPDATE player_inventory SET items = ?, currency = ?, updated_at = ? WHERE id = ?",
                (json.dumps(inventory_data.items), inventory_data.currency, now_iso(), existing["id"])
            )
        else:
            conn.execute(
                """INSERT INTO player_inventory (id, user_id, world_id, items, currency, capacity, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid4()), user_id, inventory_data.world_id, json.dumps(inventory_data.items),
                 inventory_data.currency, 50, now_iso())
            )
        conn.commit()
    
    return {"message": "Inventory updated"}


# ============ REPUTATION SYSTEM ENDPOINTS ============

@app.get("/reputation/{user_id}/{world_id}")
def get_reputation(user_id: str, world_id: str) -> Dict[str, Any]:
    """Get player's reputation with all factions"""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM player_reputation WHERE user_id = ? AND world_id = ?",
            (user_id, world_id)
        ).fetchall()
        
        reputations = []
        for row in rows:
            reputations.append({
                "faction_name": row["faction_name"],
                "reputation_points": row["reputation_points"],
                "rank": row["rank"]
            })
        
        return {"reputations": reputations}


@app.post("/reputation/update")
def update_reputation(rep_data: ReputationUpdate, user_id: str) -> Dict[str, Any]:
    """Update reputation with a faction"""
    with _get_connection() as conn:
        existing = conn.execute(
            "SELECT * FROM player_reputation WHERE user_id = ? AND world_id = ? AND faction_name = ?",
            (user_id, rep_data.world_id, rep_data.faction_name)
        ).fetchone()
        
        if existing:
            new_points = existing["reputation_points"] + rep_data.points_change
            new_rank = "hostile" if new_points < -500 else "unfriendly" if new_points < 0 else "neutral" if new_points < 500 else "friendly" if new_points < 1000 else "honored"
            
            conn.execute(
                "UPDATE player_reputation SET reputation_points = ?, rank = ?, updated_at = ? WHERE id = ?",
                (new_points, new_rank, now_iso(), existing["id"])
            )
        else:
            conn.execute(
                """INSERT INTO player_reputation (id, user_id, world_id, faction_name, reputation_points, rank, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid4()), user_id, rep_data.world_id, rep_data.faction_name, 
                 rep_data.points_change, "neutral", now_iso())
            )
        conn.commit()
    
    return {"message": "Reputation updated"}


# ============ PETS/COMPANIONS ENDPOINTS ============

@app.post("/pets/create")
def create_pet(pet_data: PetCreate, user_id: str) -> Dict[str, Any]:
    """Create/adopt a new pet"""
    pet_id = str(uuid4())
    
    with _get_connection() as conn:
        conn.execute(
            """INSERT INTO player_pets (id, user_id, world_id, pet_name, pet_type, level, stats, abilities, is_active, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (pet_id, user_id, pet_data.world_id, pet_data.pet_name, pet_data.pet_type,
             1, json.dumps(pet_data.stats), json.dumps(pet_data.abilities), 0, now_iso())
        )
        conn.commit()
    
    return {"pet_id": pet_id, "message": f"Pet {pet_data.pet_name} created!"}


@app.get("/pets/{user_id}/{world_id}")
def get_pets(user_id: str, world_id: str) -> Dict[str, Any]:
    """Get all player's pets"""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM player_pets WHERE user_id = ? AND world_id = ?",
            (user_id, world_id)
        ).fetchall()
        
        pets = []
        for row in rows:
            pets.append({
                "id": row["id"],
                "pet_name": row["pet_name"],
                "pet_type": row["pet_type"],
                "level": row["level"],
                "stats": json.loads(row["stats"]),
                "abilities": json.loads(row["abilities"]),
                "is_active": bool(row["is_active"])
            })
        
        return {"pets": pets, "total": len(pets)}


# ============ CLASS SYSTEM ENDPOINTS ============

@app.post("/class/select")
def select_class(class_data: ClassSelect, user_id: str) -> Dict[str, Any]:
    """Select player class"""
    class_id = str(uuid4())
    
    # Define class skills
    class_skills = {
        "warrior": ["shield_bash", "power_strike", "berserker_rage"],
        "mage": ["fireball", "ice_storm", "teleport"],
        "archer": ["multi_shot", "poison_arrow", "eagle_eye"],
        "rogue": ["backstab", "stealth", "smoke_bomb"]
    }
    
    skills = class_skills.get(class_data.class_name.lower(), [])
    
    with _get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM player_classes WHERE user_id = ? AND world_id = ?",
            (user_id, class_data.world_id)
        ).fetchone()
        
        if existing:
            conn.execute(
                "UPDATE player_classes SET class_name = ?, class_skills = ? WHERE id = ?",
                (class_data.class_name, json.dumps(skills), existing["id"])
            )
        else:
            conn.execute(
                """INSERT INTO player_classes (id, user_id, world_id, class_name, level, experience, class_skills, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (class_id, user_id, class_data.world_id, class_data.class_name, 1, 0, json.dumps(skills), now_iso())
            )
        conn.commit()
    
    return {"message": f"Class {class_data.class_name} selected", "skills": skills}


# ============ WORLD EVENTS ENDPOINTS ============

@app.post("/events/create")
def create_world_event(event: WorldEvent, user_id: str) -> Dict[str, Any]:
    """Create a dynamic world event"""
    event_id = str(uuid4())
    
    with _get_connection() as conn:
        conn.execute(
            """INSERT INTO world_events (id, world_id, event_type, event_name, description, start_time, end_time, event_data, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (event_id, event.world_id, event.event_type, event.event_name, event.description,
             now_iso(), None, json.dumps(event.event_data), 1)
        )
        conn.commit()
    
    return {"event_id": event_id, "message": "World event created"}


@app.get("/events/{world_id}/active")
def get_active_events(world_id: str) -> Dict[str, Any]:
    """Get all active events for a world"""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM world_events WHERE world_id = ? AND is_active = 1",
            (world_id,)
        ).fetchall()
        
        events = []
        for row in rows:
            events.append({
                "id": row["id"],
                "event_type": row["event_type"],
                "event_name": row["event_name"],
                "description": row["description"],
                "event_data": json.loads(row["event_data"])
            })
        
        return {"events": events, "total": len(events)}


# ============ CLANS/GUILDS ENDPOINTS ============

@app.post("/clans/create")
def create_clan(clan_data: ClanCreate, user_id: str) -> Dict[str, Any]:
    """Create a new clan/guild"""
    clan_id = str(uuid4())
    member_id = str(uuid4())
    
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO clans (id, name, description, leader_id, member_count, clan_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (clan_id, clan_data.name, clan_data.description, user_id, 1, 1, now_iso())
        )
        
        conn.execute(
            "INSERT INTO clan_members (id, clan_id, user_id, rank, joined_at) VALUES (?, ?, ?, ?, ?)",
            (member_id, clan_id, user_id, "leader", now_iso())
        )
        
        conn.commit()
    
    return {"clan_id": clan_id, "message": f"Clan {clan_data.name} created"}


@app.get("/clans/list")
def list_clans() -> Dict[str, Any]:
    """List all clans"""
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM clans ORDER BY clan_level DESC, member_count DESC LIMIT 50").fetchall()
        
        clans = []
        for row in rows:
            clans.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "member_count": row["member_count"],
                "clan_level": row["clan_level"]
            })
        
        return {"clans": clans}


# ============ MARKET/TRADING ENDPOINTS ============

@app.post("/market/list")
def create_market_listing(listing: MarketListing, user_id: str) -> Dict[str, Any]:
    """List an item for sale"""
    listing_id = str(uuid4())
    
    with _get_connection() as conn:
        conn.execute(
            """INSERT INTO market_listings (id, seller_id, item_id, item_name, price, quantity, description, is_sold, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (listing_id, user_id, listing.item_id, listing.item_name, listing.price, 
             listing.quantity, listing.description, 0, now_iso())
        )
        conn.commit()
    
    return {"listing_id": listing_id, "message": "Item listed for sale"}


@app.get("/market/browse")
def browse_market() -> Dict[str, Any]:
    """Browse market listings"""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM market_listings WHERE is_sold = 0 ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        
        listings = []
        for row in rows:
            listings.append({
                "id": row["id"],
                "item_name": row["item_name"],
                "price": row["price"],
                "quantity": row["quantity"],
                "description": row["description"],
                "seller_id": row["seller_id"]
            })
        
        return {"listings": listings, "total": len(listings)}


@app.post("/market/buy")
def buy_market_item(purchase: MarketPurchase, user_id: str) -> Dict[str, Any]:
    """Buy a market listing"""
    with _get_connection() as conn:
        listing = conn.execute(
            "SELECT * FROM market_listings WHERE id = ? AND is_sold = 0",
            (purchase.listing_id,)
        ).fetchone()

        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")

        if purchase.quantity > listing["quantity"]:
            raise HTTPException(status_code=400, detail="Not enough quantity")

        remaining = listing["quantity"] - purchase.quantity
        if remaining <= 0:
            conn.execute(
                "UPDATE market_listings SET quantity = 0, is_sold = 1 WHERE id = ?",
                (purchase.listing_id,)
            )
        else:
            conn.execute(
                "UPDATE market_listings SET quantity = ? WHERE id = ?",
                (remaining, purchase.listing_id),
            )

        conn.commit()

    return {
        "message": "Purchase successful",
        "item_name": listing["item_name"],
        "quantity": purchase.quantity,
        "remaining": remaining,
    }




# ============ PLAYER STATISTICS ENDPOINTS ============

@app.get("/stats/{user_id}")
def get_player_stats(user_id: str) -> Dict[str, Any]:
    """Get player statistics"""
    with _get_connection() as conn:
        stats = conn.execute(
            "SELECT * FROM player_stats WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if not stats:
            return {
                "total_playtime": 0,
                "enemies_defeated": 0,
                "distance_traveled": 0.0,
                "items_collected": 0,
                "quests_completed": 0,
                "deaths": 0,
                "worlds_created": 0,
                "achievements_unlocked": 0
            }
        
        return {
            "total_playtime": stats["total_playtime"],
            "enemies_defeated": stats["enemies_defeated"],
            "distance_traveled": stats["distance_traveled"],
            "items_collected": stats["items_collected"],
            "quests_completed": stats["quests_completed"],
            "deaths": stats["deaths"],
            "worlds_created": stats["worlds_created"],
            "achievements_unlocked": stats["achievements_unlocked"]
        }


@app.post("/stats/update")
def update_player_stats(user_id: str, stat_updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update player statistics"""
    with _get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM player_stats WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if existing:
            # Build UPDATE query dynamically
            updates = []
            values = []
            for key, value in stat_updates.items():
                updates.append(f"{key} = ?")
                values.append(value)
            
            values.extend([now_iso(), existing["id"]])
            
            conn.execute(
                f"UPDATE player_stats SET {', '.join(updates)}, updated_at = ? WHERE id = ?",
                values
            )
        else:
            # Create new stats entry
            conn.execute(
                """INSERT INTO player_stats 
                   (id, user_id, total_playtime, enemies_defeated, distance_traveled, items_collected, 
                    quests_completed, deaths, worlds_created, achievements_unlocked, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid4()), user_id, 
                 stat_updates.get("total_playtime", 0),
                 stat_updates.get("enemies_defeated", 0),
                 stat_updates.get("distance_traveled", 0.0),
                 stat_updates.get("items_collected", 0),
                 stat_updates.get("quests_completed", 0),
                 stat_updates.get("deaths", 0),
                 stat_updates.get("worlds_created", 0),
                 stat_updates.get("achievements_unlocked", 0),
                 now_iso())
            )
        conn.commit()
    
    return {"message": "Statistics updated"}


# ============ SETTINGS/ACCESSIBILITY ENDPOINTS ============

@app.get("/settings/{user_id}")
def get_user_settings(user_id: str) -> Dict[str, Any]:
    """Get user settings"""
    with _get_connection() as conn:
        settings = conn.execute(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if not settings:
            return {
                "graphics_quality": "medium",
                "audio_volume": 1.0,
                "music_volume": 0.7,
                "sfx_volume": 1.0,
                "colorblind_mode": "none",
                "subtitle_size": "medium",
                "controls_config": {}
            }
        
        return {
            "graphics_quality": settings["graphics_quality"],
            "audio_volume": settings["audio_volume"],
            "music_volume": settings["music_volume"],
            "sfx_volume": settings["sfx_volume"],
            "colorblind_mode": settings["colorblind_mode"],
            "subtitle_size": settings["subtitle_size"],
            "controls_config": json.loads(settings["controls_config"]) if settings["controls_config"] else {}
        }


@app.post("/settings/update")
def update_settings(settings_data: SettingsUpdate, user_id: str) -> Dict[str, Any]:
    """Update user settings"""
    with _get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM user_settings WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        updates = {}
        if settings_data.graphics_quality: updates["graphics_quality"] = settings_data.graphics_quality
        if settings_data.audio_volume is not None: updates["audio_volume"] = settings_data.audio_volume
        if settings_data.music_volume is not None: updates["music_volume"] = settings_data.music_volume
        if settings_data.sfx_volume is not None: updates["sfx_volume"] = settings_data.sfx_volume
        if settings_data.colorblind_mode: updates["colorblind_mode"] = settings_data.colorblind_mode
        if settings_data.subtitle_size: updates["subtitle_size"] = settings_data.subtitle_size
        if settings_data.controls_config: updates["controls_config"] = json.dumps(settings_data.controls_config)
        
        if existing:
            update_parts = [f"{k} = ?" for k in updates.keys()]
            values = list(updates.values()) + [now_iso(), existing["id"]]
            
            conn.execute(
                f"UPDATE user_settings SET {', '.join(update_parts)}, updated_at = ? WHERE id = ?",
                values
            )
        else:
            conn.execute(
                """INSERT INTO user_settings 
                   (id, user_id, graphics_quality, audio_volume, music_volume, sfx_volume, 
                    colorblind_mode, subtitle_size, controls_config, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid4()), user_id,
                 settings_data.graphics_quality or "medium",
                 settings_data.audio_volume if settings_data.audio_volume is not None else 1.0,
                 settings_data.music_volume if settings_data.music_volume is not None else 0.7,
                 settings_data.sfx_volume if settings_data.sfx_volume is not None else 1.0,
                 settings_data.colorblind_mode or "none",
                 settings_data.subtitle_size or "medium",
                 json.dumps(settings_data.controls_config) if settings_data.controls_config else None,
                 now_iso())
            )
        conn.commit()
    
    return {"message": "Settings updated"}


# ============ WORLD TEMPLATES ENDPOINTS ============

@app.post("/templates/create")
def create_template(template: TemplateCreate, user_id: str) -> Dict[str, Any]:
    """Create a world template"""
    template_id = str(uuid4())
    
    with _get_connection() as conn:
        conn.execute(
            """INSERT INTO world_templates (id, name, description, category, template_data, thumbnail_url, usage_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (template_id, template.name, template.description, template.category,
             json.dumps(template.template_data), template.thumbnail_url, 0, now_iso())
        )
        conn.commit()
    
    return {"template_id": template_id, "message": "Template created"}


@app.get("/templates/list")
def list_templates() -> Dict[str, Any]:
    """List all world templates"""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM world_templates ORDER BY usage_count DESC"
        ).fetchall()
        
        templates = []
        for row in rows:
            templates.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "category": row["category"],
                "thumbnail_url": row["thumbnail_url"],
                "usage_count": row["usage_count"]
            })
        
        return {"templates": templates, "total": len(templates)}


@app.get("/templates/{template_id}")
def get_template(template_id: str) -> Dict[str, Any]:
    """Get a specific template"""
    with _get_connection() as conn:
        template = conn.execute(
            "SELECT * FROM world_templates WHERE id = ?",
            (template_id,)
        ).fetchone()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Increment usage count
        conn.execute(
            "UPDATE world_templates SET usage_count = usage_count + 1 WHERE id = ?",
            (template_id,)
        )
        conn.commit()
        
        return {
            "id": template["id"],
            "name": template["name"],
            "description": template["description"],
            "category": template["category"],
            "template_data": json.loads(template["template_data"]),
            "thumbnail_url": template["thumbnail_url"]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)