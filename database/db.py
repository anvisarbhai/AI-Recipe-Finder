"""
database/db.py
─────────────────────────────────────────────────────────────────
Handles all SQLite operations:
  • Creating tables on first run
  • Saving / removing bookmarked recipes
  • Fetching the saved-recipe list for the current session
─────────────────────────────────────────────────────────────────
"""
import sqlite3
import json
from pathlib import Path

# Always store the DB file next to this module
DB_PATH = Path(__file__).parent / "recipes.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection with row_factory so rows behave like dicts."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create the `saved_recipes` table if it doesn't already exist.
    Called once at app start-up.
    """
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_recipes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id   INTEGER UNIQUE NOT NULL,
                title       TEXT    NOT NULL,
                image       TEXT,
                data        TEXT,          -- full JSON blob of the recipe
                saved_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_recipe(recipe: dict) -> bool:
    """
    Insert a recipe into the database.
    Returns True on success, False if it was already saved.
    """
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO saved_recipes (recipe_id, title, image, data) VALUES (?, ?, ?, ?)",
                (recipe["id"], recipe["title"], recipe.get("image", ""), json.dumps(recipe)),
            )
            conn.commit()
        return True
    except Exception:
        return False


def remove_recipe(recipe_id: int) -> None:
    """Delete a saved recipe by its Spoonacular ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM saved_recipes WHERE recipe_id = ?", (recipe_id,))
        conn.commit()


def get_saved_recipes() -> list[dict]:
    """Return all saved recipes as a list of dicts."""
    with get_connection() as conn:
        rows = conn.execute("SELECT data FROM saved_recipes ORDER BY saved_at DESC").fetchall()
    return [json.loads(row["data"]) for row in rows]


def is_saved(recipe_id: int) -> bool:
    """Return True if the recipe is already bookmarked."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM saved_recipes WHERE recipe_id = ?", (recipe_id,)
        ).fetchone()
    return row is not None
