"""
app.py  —  AI-Powered Recipe Finder & Smart Cooking Assistant
═══════════════════════════════════════════════════════════════
Entry point for the Streamlit application.

Run locally:
    streamlit run app.py

Project layout:
    app.py              ← YOU ARE HERE
    requirements.txt    ← Python dependencies
    .env                ← API keys (never commit this)
    styles/             ← Custom CSS
    components/         ← Reusable UI pieces (recipe card, etc.)
    utils/              ← API calls, chatbot wrapper
    models/             ← TF-IDF recommendation engine
    database/           ← SQLite persistence
    pages/              ← Streamlit multi-page stubs
═══════════════════════════════════════════════════════════════
"""

import streamlit as st

# ── Page config MUST be the very first Streamlit call ────────────
st.set_page_config(
    page_title="RecipeAI – Smart Cooking Assistant",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load project modules ─────────────────────────────────────────
import streamlit as st
import os
# API Keys from Streamlit Secrets
SPOONACULAR_API_KEY = st.secrets["80a99561ad3d415fb58cdc49a34cb3b2"]
GEMINI_API_KEY = st.secrets["AIzaSyDBBmBB5tUeOmw3rVstl4ltgHwEvOOcjbw"]
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))   # ensure local imports work

from styles      import MAIN_CSS
from utils       import search_recipes, chat_with_chef
from models      import rank_recipes, normalise_list
from database    import init_db, get_saved_recipes
from components  import render_recipe_card

# ── One-time DB initialisation ───────────────────────────────────
init_db()

# ── Inject custom CSS ────────────────────────────────────────────
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════
CUISINES = [
    "", "Indian", "Italian", "Chinese", "Mexican",
    "Thai", "Japanese", "Mediterranean", "American",
    "French", "Greek", "Spanish", "Middle Eastern",
]
DIETS = [
    "", "Vegetarian", "Vegan", "Gluten Free",
    "Ketogenic", "Paleo", "Whole30", "Dairy Free",
]
MEAL_TYPES = ["", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert"]
TIME_OPTIONS = {
    "Any time": 0,
    "Under 15 min ⚡": 15,
    "Under 30 min 🕐": 30,
    "Under 60 min 🕐": 60,
}

# ═══════════════════════════════════════════════════════════════
# SESSION STATE  (persisted across Streamlit reruns)
# ═══════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "recipes":    [],
        "searched":   False,
        "dark_mode":  False,
        "chat_history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ═══════════════════════════════════════════════════════════════
# DARK MODE TOGGLE
# ═══════════════════════════════════════════════════════════════
with st.container():
    col_logo, col_dark = st.columns([8, 1])
    with col_dark:
        dm_label = "☀️ Light" if st.session_state.dark_mode else "🌙 Dark"
        if st.button(dm_label, key="dark_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

# Apply dark-mode body class via JS (Streamlit doesn't expose the HTML attr natively)
if st.session_state.dark_mode:
    st.markdown("""
    <script>
    document.body.setAttribute('data-theme','dark');
    document.body.style.setProperty('--bg','#121110');
    </script>
    <style>
    body, [class*="css"], .stApp {
        background-color:#121110 !important;
        color:#f0ede8 !important;
    }
    .recipe-card, .search-panel, .nutrition-card {
        background:#1e1c1a !important;
        border-color:rgba(255,255,255,0.08) !important;
    }
    </style>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <p class="hero-badge">✦ AI-POWERED COOKING ASSISTANT</p>
  <h1 class="hero-title">Turn any ingredients into<br><span>incredible meals</span></h1>
  <p class="hero-sub">Tell us what's in your fridge. Our AI finds the best matching recipes,
  calculates missing ingredients, and even chats with you about substitutions.</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════
tab_search, tab_saved, tab_chat = st.tabs(["🔍 Find Recipes", "🔖 Saved Recipes", "🤖 AI Chef Chat"])

# ───────────────────────────────────────────────────────────────
# TAB 1 – FIND RECIPES
# ───────────────────────────────────────────────────────────────
with tab_search:

    # ── Search Panel ─────────────────────────────────────────────
    st.markdown('<div class="search-panel">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🥕 What ingredients do you have?</p>', unsafe_allow_html=True)

    with st.form("search_form"):
        # Row 1: ingredient input + voice hint
        ingredient_input = st.text_input(
            label="Ingredients",
            placeholder="e.g. chicken, tomato, garlic, lemon …",
            label_visibility="collapsed",
        )
        # Info about voice
        st.caption("💡 Tip: separate ingredients with commas.  "
                   "Regional names work too — try 'paneer', 'capsicum', 'curd'.")

        # Row 2: filters
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            cuisine = st.selectbox("Cuisine", CUISINES, index=0)
        with c2:
            diet = st.selectbox("Diet", DIETS, index=0)
        with c3:
            meal_type = st.selectbox("Meal type", MEAL_TYPES, index=0)
        with c4:
            time_label = st.selectbox("Cooking time", list(TIME_OPTIONS.keys()), index=0)

        submitted = st.form_submit_button("🔍 Find Recipes", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Handle form submission ────────────────────────────────────
    if submitted:
        raw_ingredients = [i.strip() for i in ingredient_input.split(",") if i.strip()]

        if not raw_ingredients:
            st.warning("Please enter at least one ingredient.")
        else:
            normalised = normalise_list(raw_ingredients)
            if normalised != raw_ingredients:
                translated = [f"{o}→{n}" for o, n in zip(raw_ingredients, normalised) if o != n]
                if translated:
                    st.info(f"🔄 Ingredient translation: {', '.join(translated)}")

            max_time = TIME_OPTIONS[time_label]

            with st.spinner("🔎 Searching recipes …"):
                raw_recipes = search_recipes(
                    ingredients=normalised,
                    cuisine=cuisine,
                    diet=diet,
                    meal_type=meal_type,
                    max_ready_time=max_time,
                    number=16,
                )

            if raw_recipes:
                with st.spinner("🤖 AI ranking your recipes …"):
                    ranked = rank_recipes(raw_recipes, normalised)
                st.session_state.recipes  = ranked
                st.session_state.searched = True
                st.success(f"✅ Found {len(ranked)} recipes — ranked by AI match score")
            else:
                st.session_state.recipes  = []
                st.session_state.searched = True
                st.error("😕 No recipes found. Try different ingredients or relax the filters.")

    # ── Results grid ──────────────────────────────────────────────
    if st.session_state.searched and st.session_state.recipes:
        recipes = st.session_state.recipes

        # Quick summary stats
        avg_score = sum(r.get("ai_score", 0) for r in recipes) / len(recipes)
        avg_time  = sum(r.get("readyInMinutes", 0) or 0 for r in recipes) / len(recipes)

        m1, m2, m3 = st.columns(3)
        m1.metric("Recipes Found",    len(recipes))
        m2.metric("Avg AI Score",     f"{avg_score:.0%}")
        m3.metric("Avg Cook Time",    f"{avg_time:.0f} min")

        st.markdown("<hr style='border-color:var(--border);margin:1.5rem 0'>", unsafe_allow_html=True)
        st.markdown('<p class="section-title">✨ Top Matches</p>', unsafe_allow_html=True)

        # 3-column card grid
        cols = st.columns(3, gap="medium")
        for i, recipe in enumerate(recipes):
            with cols[i % 3]:
                render_recipe_card(recipe, i)
                st.markdown("<br>", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# TAB 2 – SAVED RECIPES
# ───────────────────────────────────────────────────────────────
with tab_saved:
    saved_list = get_saved_recipes()

    if not saved_list:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:var(--text-muted)">
          <div style="font-size:3rem;margin-bottom:1rem">🔖</div>
          <p style="font-size:1.1rem;font-weight:600">No saved recipes yet</p>
          <p>Find a recipe you love and tap <strong>Save recipe</strong> to bookmark it here.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="section-title">🔖 Your Saved Recipes ({len(saved_list)})</p>',
                    unsafe_allow_html=True)
        cols = st.columns(3, gap="medium")
        for i, recipe in enumerate(saved_list):
            with cols[i % 3]:
                render_recipe_card(recipe, f"saved_{i}")
                st.markdown("<br>", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# TAB 3 – AI CHEF CHAT
# ───────────────────────────────────────────────────────────────
with tab_chat:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a1814,#2d2520);border-radius:var(--radius);
    padding:1.5rem 2rem;margin-bottom:1.5rem">
      <p style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:700;
      color:#f0ede8;margin:0 0 0.3rem 0">🤖 ChefBot — Your AI Cooking Assistant</p>
      <p style="color:#9e9890;font-size:0.9rem;margin:0">Ask me anything: ingredient swaps,
      healthier versions, spice levels, meal ideas, nutrition questions …</p>
    </div>
    """, unsafe_allow_html=True)

    # Suggested prompts
    st.markdown("**💡 Try asking:**")
    sugg_cols = st.columns(3)
    suggestions = [
        "What can I substitute for eggs?",
        "Make this recipe vegan",
        "Low-carb alternatives to rice?",
        "How do I reduce spice in curry?",
        "Best protein-rich breakfast ideas",
        "What pairs well with salmon?",
    ]
    for i, s in enumerate(suggestions):
        with sugg_cols[i % 3]:
            if st.button(s, key=f"sugg_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": s})
                with st.spinner("ChefBot is thinking …"):
                    reply = chat_with_chef(s, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

    st.markdown("<hr style='border-color:var(--border);margin:1rem 0'>", unsafe_allow_html=True)

    # Chat history
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div style="display:flex;justify-content:flex-end">'
                    f'<div class="chat-bubble-user">{msg["content"]}</div></div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="chat-bubble-bot">🤖 {msg["content"]}</div>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Input row
    chat_col, clear_col = st.columns([5, 1])
    with chat_col:
        user_input = st.text_input(
            "Message ChefBot",
            placeholder="Ask anything about cooking …",
            label_visibility="collapsed",
            key="chat_input",
        )
    with clear_col:
        if st.button("🗑️ Clear", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("ChefBot is thinking …"):
            reply = chat_with_chef(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:1.5rem;color:var(--text-muted);
font-size:0.8rem;border-top:1px solid var(--border)">
  Built with ❤️ using Streamlit · Powered by Spoonacular API & Google Gemini<br>
  <span style="opacity:0.6">RecipeAI — AI-Powered Smart Cooking Assistant</span>
</div>
""", unsafe_allow_html=True)
