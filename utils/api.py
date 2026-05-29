"""
utils/api.py  —  Spoonacular FREE plan, FIXED ingredient matching
"""
import os, requests, streamlit as st


BASE = "https://api.spoonacular.com"

# ── Strict diet exclusion lists ───────────────────────────────────
# EGGS are NON-VEG — excluded from both vegetarian and vegan
DIET_EXCLUDE = {
    "vegetarian": [
        "chicken","beef","pork","fish","salmon","tuna","shrimp","prawn",
        "lamb","turkey","bacon","ham","sausage","meat","seafood","crab",
        "lobster","anchovy","anchovies","egg","eggs","egg white","egg yolk",
    ],
    "vegan": [
        "chicken","beef","pork","fish","salmon","tuna","shrimp","prawn",
        "lamb","turkey","bacon","ham","sausage","meat","seafood","crab",
        "lobster","anchovy","anchovies","egg","eggs","egg white","egg yolk",
        "milk","cheese","butter","cream","yogurt","ghee","whey","casein",
        "honey","gelatin","lard","mayonnaise","parmesan","mozzarella",
        "cheddar","brie","feta","ricotta","cream cheese",
    ],
    "gluten free": [
        "flour","bread","pasta","wheat","barley","rye","soy sauce",
        "beer","breadcrumbs","croutons","couscous","semolina","spelt",
    ],
    "ketogenic": [
        "sugar","flour","bread","pasta","rice","potato","corn","oats",
        "honey","maple syrup","banana","apple","orange","grape","mango",
        "beans","lentils","chickpeas","cereal","granola",
    ],
    "dairy free": [
        "milk","cheese","butter","cream","yogurt","ghee","whey","casein",
        "parmesan","mozzarella","cheddar","brie","feta","ricotta",
        "cream cheese","sour cream","half and half","condensed milk",
    ],
}

def _key() -> str:
    
    try:
        k = st.secrets.get("SPOONACULAR_API_KEY", "")
        if k and "placeholder" not in k.lower() and k != "your_spoonacular_api_key_here":
            return k
    except Exception:
        pass
    k = os.getenv("SPOONACULAR_API_KEY", "")
    return k

def _passes_diet(recipe: dict, diet: str) -> bool:
    if not diet:
        return True
    banned = DIET_EXCLUDE.get(diet.lower(), [])
    if not banned:
        return True
    # Collect all ingredient names from all possible fields
    names = []
    for field in ("usedIngredients","missedIngredients","extendedIngredients"):
        for item in recipe.get(field, []):
            names.append(item.get("name","").lower())
            names.append((item.get("nameClean") or "").lower())
            names.append((item.get("original") or "").lower())
    all_text = " ".join(names)
    return not any(b in all_text for b in banned)

def search_recipes(
    ingredients: list,
    cuisine: str = "",
    diet: str = "",
    meal_type: str = "",
    max_ready_time: int = 0,
    number: int = 16,
    offset: int = 0,
) -> list:

    api_key = _key()

    if not api_key:
        st.error("🔑 API key not found.")
        return []

    query_string = " ".join(ingredients)

    params = {
        "apiKey": api_key,
        "query": query_string,
        "fillIngredients": True,
        "addRecipeInformation": True,
        "number": 50,
        "offset": offset,
        "sort": "relevance",
        "sortDirection": "desc",
        "instructionsRequired": True,
    }

    if cuisine:
        params["cuisine"] = cuisine

        

    VALID_DIETS = [ 
        "vegetarian",
    "vegan",
    "gluten free",
    "ketogenic",
    "dairy free",
    ]
    if diet and diet.lower() in VALID_DIETS:
     params["diet"] = diet.lower()
        

    if meal_type:
        params["type"] = meal_type.lower()

    if max_ready_time:
        params["maxReadyTime"] = max_ready_time

    try:

        r = requests.get(
            f"{BASE}/recipes/complexSearch",
            params=params,
            timeout=15,
        )

        r.raise_for_status()

        results = r.json().get("results", [])

    except Exception as e:

        st.error(f"API error: {e}")

        return []

    if not results:
        return []

    # ── safer diet filtering ─────────────────────

    if diet and diet.lower() in ["vegetarian", "vegan"]:

        filtered = [
            recipe
            for recipe in results
            if _passes_diet(recipe, diet)
        ]

        if filtered:
            results = filtered

    # ── safer cooking time filtering ─────────────

    if max_ready_time:

        filtered = [
            recipe
            for recipe in results
            if (recipe.get("readyInMinutes") or 999)
            <= max_ready_time
        ]

        if filtered:
            results = filtered

    return results[:number]

def get_recipe_details(recipe_id: int) -> dict | None:
    api_key = _key()
    if not api_key:
        return None
    try:
        r = requests.get(
            f"{BASE}/recipes/{recipe_id}/information",
            params={"apiKey": api_key, "includeNutrition": True},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None