import os
import requests
import streamlit as st
from dotenv import load_dotenv

BASE_URL = "https://api.spoonacular.com"

def _key():
    load_dotenv(override=True)
    key = os.getenv("SPOONACULAR_API_KEY", "")
    return key

def search_recipes(ingredients, cuisine="", diet="", meal_type="", max_ready_time=0, number=12):
    api_key = _key()
    if not api_key or api_key == "your_spoonacular_api_key_here":
        st.error("API key not loaded. Check .env file.")
        st.write("DEBUG key value:", repr(api_key))
        return []

    params = {
        "apiKey": api_key,
        "ingredients": ",".join(ingredients),
        "number": number,
        "ranking": 1,
        "ignorePantry": True,
    }

    try:
        resp = requests.get(f"{BASE_URL}/recipes/findByIngredients", params=params, timeout=15)
        resp.raise_for_status()
        basic_recipes = resp.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"API error {resp.status_code}: {e}")
        return []
    except Exception as e:
        st.error(f"Connection error: {e}")
        return []

    if not basic_recipes:
        return []

    ids = ",".join(str(r["id"]) for r in basic_recipes)
    try:
        info_resp = requests.get(
            f"{BASE_URL}/recipes/informationBulk",
            params={"apiKey": api_key, "ids": ids},
            timeout=15,
        )
        info_resp.raise_for_status()
        info_map = {r["id"]: r for r in info_resp.json()}
    except Exception:
        info_map = {}

    merged = []
    for r in basic_recipes:
        extra = info_map.get(r["id"], {})
        merged.append({**r, **extra})

    if max_ready_time:
        merged = [r for r in merged if (r.get("readyInMinutes") or 999) <= max_ready_time]

    return merged

def get_recipe_details(recipe_id):
    api_key = _key()
    if not api_key:
        return None
    try:
        resp = requests.get(
            f"{BASE_URL}/recipes/{recipe_id}/information",
            params={"apiKey": api_key},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None