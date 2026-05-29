"""
models/recommender.py
Smart AI recipe ranking engine
"""

import re

# ─────────────────────────────────────────────
# INGREDIENT SYNONYMS
# ─────────────────────────────────────────────

SYNONYMS = {
    "capsicum": "bell pepper",
    "curd": "yogurt",
    "aubergine": "eggplant",
    "courgette": "zucchini",
    "coriander": "cilantro",
    "spring onion": "scallion",
    "brinjal": "eggplant",
    "lady finger": "okra",
    "karela": "bitter melon",
    "shimla mirch": "bell pepper",
    "maida": "all purpose flour",
    "besan": "chickpea flour",
    "dal": "lentils",
    "chana": "chickpeas",
    "rajma": "kidney beans",
    "methi": "fenugreek",
    "jeera": "cumin",
    "haldi": "turmeric",
    "mirchi": "chili pepper",
    "hari mirch": "green chili",
}

# ─────────────────────────────────────────────
# NORMALISE INGREDIENTS
# ─────────────────────────────────────────────

def normalise(ing: str) -> str:

    s = ing.strip().lower()

    for alias, canon in SYNONYMS.items():

        s = re.sub(
            rf"\b{re.escape(alias)}\b",
            canon,
            s
        )

    return s


def normalise_list(ings: list) -> list:

    return [
        normalise(i)
        for i in ings
        if i.strip()
    ]


# ─────────────────────────────────────────────
# MAIN RANKING FUNCTION
# ─────────────────────────────────────────────

def rank_recipes(
    recipes: list,
    user_ingredients: list
) -> list:

    if not recipes:
        return []

    user_norm = normalise_list(user_ingredients)

    ranked = []

    for rec in recipes:

        title = rec.get("title", "").lower()

        # collect recipe ingredient text
        recipe_ingredients = []

        for field in [
            "extendedIngredients",
            "usedIngredients",
            "missedIngredients"
        ]:

            for item in rec.get(field, []):

                name = (
                    item.get("name")
                    or item.get("originalName")
                    or item.get("original")
                    or ""
                ).lower()

                if name:
                    recipe_ingredients.append(name)

        all_text = (
            title
            + " "
            + " ".join(recipe_ingredients)
        ).lower()

        # ─────────────────────────────────────
        # AI SCORING
        # ─────────────────────────────────────

        title_score = 0
        ingredient_score = 0

        for ing in user_norm:

            # title relevance
            if re.search(
                rf"\b{re.escape(ing)}\b",
                title
            ):
                title_score += 5

            # ingredient relevance
            if re.search(
                rf"\b{re.escape(ing)}\b",
                all_text
            ):
                ingredient_score += 3

        # health bonus
        health = float(
            rec.get("healthScore", 0) or 0
        )

        health_bonus = 0

        if health >= 70:
            health_bonus = 2

        elif health >= 40:
            health_bonus = 1

        # cooking speed bonus
        ready = rec.get(
            "readyInMinutes",
            999
        )

        speed_bonus = 0

        if ready <= 20:
            speed_bonus = 2

        elif ready <= 40:
            speed_bonus = 1

        final_score = (
            title_score
            + ingredient_score
            + health_bonus
            + speed_bonus
        )

        # ─────────────────────────────────────
        # INGREDIENT MATCH %
        # ─────────────────────────────────────

        matches = 0

        search_text = (
            title
            + " "
            + " ".join(recipe_ingredients)
        ).lower()

        for ing in user_norm:

            pattern = rf"\b{re.escape(ing)}\b"

            if re.search(pattern, search_text):

                matches += 1

        match_pct = round(
            (
                matches
                / max(len(user_norm), 1)
            ) * 100
        )

        # ─────────────────────────────────────
        # MISSING INGREDIENTS
        # ─────────────────────────────────────

        needed = set()

        for item in rec.get(
            "missedIngredients",
            []
        ):

            n = normalise(
                item.get("nameClean")
                or item.get("name", "")
            )

            if n:
                needed.add(n)

        missing = sorted(
            needed - set(user_norm)
        )

        ranked.append({
            **rec,
            "ai_score": round(final_score, 2),
            "missing_items": missing,
            "match_pct": match_pct,
        })

    # ─────────────────────────────────────────
    # SORT BEST RECIPES FIRST
    # ─────────────────────────────────────────

    ranked.sort(
        key=lambda r: r["ai_score"],
        reverse=True
    )

    return ranked