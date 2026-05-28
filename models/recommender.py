"""
models/recommender.py
─────────────────────────────────────────────────────────────────
Smart AI recommendation engine.

How it works (plain English):
1. Ingredient normalisation  — "capsicum" → "bell pepper" so we match
   correctly even when users type regional names.
2. TF-IDF vectorisation      — each recipe's ingredient list is turned
   into a numeric vector that captures which ingredients are rare vs
   common across all recipes.
3. Cosine similarity         — measures how "close" the user's ingredient
   vector is to each recipe's vector (1.0 = perfect match, 0 = nothing
   in common).
4. Weighted scoring          — blends four signals into a final score:
     • ingredient match  50 %
     • health score      20 %
     • cooking speed     15 %
     • popularity        15 %
5. Missing-ingredient calc   — for each top recipe we report which
   ingredients the user still needs to buy.
─────────────────────────────────────────────────────────────────
"""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Synonym / regional-name map ──────────────────────────────────
# Add more pairs here as needed; keys are what users type, values
# are canonical ingredient names used in most English recipe APIs.
SYNONYMS: dict[str, str] = {
    "paneer":      "cottage cheese",
    "capsicum":    "bell pepper",
    "curd":        "yogurt",
    "aubergine":   "eggplant",
    "courgette":   "zucchini",
    "coriander":   "cilantro",
    "spring onion":"scallion",
    "brinjal":     "eggplant",
    "lady finger": "okra",
    "karela":      "bitter melon",
    "shimla mirch":"bell pepper",
    "maida":       "all purpose flour",
    "besan":       "chickpea flour",
    "dal":         "lentils",
    "chana":       "chickpeas",
    "rajma":       "kidney beans",
    "methi":       "fenugreek",
    "jeera":       "cumin",
    "haldi":       "turmeric",
    "mirchi":      "chili pepper",
    "hari mirch":  "green chili",
}


def normalise(ingredient: str) -> str:
    """
    Lowercase, strip whitespace, apply synonym map.
    Example:  "  Capsicum  " → "bell pepper"
    """
    cleaned = ingredient.strip().lower()
    # replace multi-word synonyms first, then single-word
    for alias, canonical in SYNONYMS.items():
        cleaned = re.sub(rf"\b{re.escape(alias)}\b", canonical, cleaned)
    return cleaned


def normalise_list(ingredients: list[str]) -> list[str]:
    return [normalise(i) for i in ingredients if i.strip()]


def _extract_ingredient_text(recipe: dict) -> str:
    """Pull all ingredient names from a Spoonacular recipe dict into one string."""
    parts: list[str] = []

    # usedIngredients / missedIngredients lists
    for key in ("usedIngredients", "missedIngredients", "extendedIngredients"):
        for item in recipe.get(key, []):
            name = item.get("nameClean") or item.get("name", "")
            if name:
                parts.append(normalise(name))

    # fallback: title tokens
    if not parts:
        parts = recipe.get("title", "").lower().split()

    return " ".join(parts)


def rank_recipes(recipes: list[dict], user_ingredients: list[str]) -> list[dict]:
    """
    Given a list of raw Spoonacular recipe dicts and the user's ingredient list,
    return the same list sorted by our weighted AI score (highest first).
    Each recipe dict gets two extra keys added:
        • ai_score         (float 0–1)
        • missing_items    (list[str])
    """
    if not recipes:
        return []

    normalised_user = normalise_list(user_ingredients)
    user_text = " ".join(normalised_user)

    # ── Build corpus for TF-IDF ──────────────────────────────────
    corpus: list[str] = [_extract_ingredient_text(r) for r in recipes]
    corpus_with_user = corpus + [user_text]   # user query appended last

    vectoriser = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectoriser.fit_transform(corpus_with_user)

    # user vector is the last row
    user_vec   = tfidf_matrix[-1]
    recipe_vecs = tfidf_matrix[:-1]

    # cosine similarity between user and every recipe
    similarities = cosine_similarity(user_vec, recipe_vecs).flatten()

    # ── Compute each normalised sub-score ────────────────────────
    max_time   = max((r.get("readyInMinutes", 60) or 60) for r in recipes) or 60
    max_pop    = max((r.get("aggregateLikes",  0)  or 0 ) for r in recipes) or 1

    scored: list[dict] = []
    for i, recipe in enumerate(recipes):
        ingredient_score = float(similarities[i])

        health_raw  = float(recipe.get("healthScore", 0) or 0) / 100.0
        time_raw    = float(recipe.get("readyInMinutes", 60) or 60)
        speed_score = 1.0 - (time_raw / max_time)          # faster = higher score
        pop_raw     = float(recipe.get("aggregateLikes", 0) or 0)
        pop_score   = pop_raw / max_pop

        # Weighted blend
        ai_score = (
            0.50 * ingredient_score
            + 0.20 * health_raw
            + 0.15 * speed_score
            + 0.15 * pop_score
        )

        # ── Missing ingredients ───────────────────────────────────
        needed = set()
        for item in recipe.get("missedIngredients", []):
            name = normalise(item.get("nameClean") or item.get("name", ""))
            if name:
                needed.add(name)
        missing_items = sorted(needed - set(normalised_user))

        recipe = {**recipe, "ai_score": round(ai_score, 4), "missing_items": missing_items}
        scored.append(recipe)

    # Sort descending by ai_score
    scored.sort(key=lambda r: r["ai_score"], reverse=True)
    return scored
