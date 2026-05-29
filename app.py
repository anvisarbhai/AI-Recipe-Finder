"""
app.py  —  RecipeAI  (production-ready, light theme only)
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

st.set_page_config(
    page_title="RecipeAI – Smart Cooking Assistant",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from styles     import MAIN_CSS
from utils      import search_recipes, chat_with_chef
from models     import rank_recipes, normalise_list
from database   import init_db, get_saved_recipes
from components import render_recipe_card

init_db()
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────
CUISINES   = ["","Indian","Italian","Chinese","Mexican","Thai",
               "Japanese","Mediterranean","American","French","Greek","Spanish"]
DIETS      = ["","Vegetarian","Vegan","Gluten Free","Ketogenic","Dairy Free","Paleo"]
MEAL_TYPES = ["","Breakfast","Lunch","Dinner","Snack","Dessert","Soup"]
TIME_MAP   = {"Any time":0,"Under 15 min ⚡":15,"Under 30 min":30,"Under 60 min":60}
TRENDING   = ["pasta","avocado toast","butter chicken","tacos","sushi",
               "ramen","shakshuka","pad thai","biryani","tiramisu"]
SUGGESTIONS= ["What can I substitute for eggs?","Make this recipe vegan",
               "Low-carb alternatives to rice?","How to reduce spice in curry?",
               "Best high-protein breakfast ideas","What pairs well with salmon?"]

# ── Session state ─────────────────────────────────────────────────
for k,v in {"recipes":[],"searched":False,"page":0,
            "last_ingredients":[],"search_history":[],"chat":[]}.items():
    if k not in st.session_state:
        st.session_state[k] = v

PAGE_SIZE = 9   # cards per page

# ── Hero ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-badge">✦ AI-POWERED COOKING ASSISTANT</p>
  <h1 class="hero-title">Turn any ingredients into<br><span>incredible meals</span></h1>
  <p class="hero-sub">Tell us what's in your fridge — our AI finds the best matching
  recipes, shows missing ingredients, and even chats with you about substitutions.</p>
</div>""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────
tab_search, tab_saved, tab_chat, tab_random = st.tabs(
    ["🔍 Find Recipes","🔖 Saved","🤖 AI Chef","🎲 Random"])

# ══════════════════════════════════════════════════════════════════
# TAB 1  —  FIND RECIPES
# ══════════════════════════════════════════════════════════════════
with tab_search:

    # ── Trending chips ────────────────────────────────────────────
    st.markdown("**🔥 Trending searches:**")
    tcols = st.columns(len(TRENDING))
    for i,t in enumerate(TRENDING):
        with tcols[i]:
            if st.button(t, key=f"trend_{i}"):
                st.session_state["_prefill"] = t

    # ── Search form ───────────────────────────────────────────────
    st.markdown('<div class="search-panel">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🥕 What ingredients do you have?</p>',
                unsafe_allow_html=True)

    prefill = st.session_state.pop("_prefill","")

    with st.form("search_form"):
        ing_input = st.text_input(
            "Ingredients", value=prefill,
            placeholder="e.g.  chicken, tomato, garlic, lemon …",
            label_visibility="collapsed")
        st.caption("💡 Separate with commas. Regional names work: paneer, capsicum, curd …")

        c1,c2,c3,c4 = st.columns(4)
        cuisine   = c1.selectbox("Cuisine",   CUISINES,   index=0)
        diet      = c2.selectbox("Diet",      DIETS,      index=0)
        meal_type = c3.selectbox("Meal type", MEAL_TYPES, index=0)
        time_lbl  = c4.selectbox("Time",      list(TIME_MAP.keys()), index=0)
        submitted = st.form_submit_button("🔍 Find Recipes", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Handle search ─────────────────────────────────────────────
    if submitted:
        raw  = [i.strip() for i in ing_input.split(",") if i.strip()]
        if not raw:
            st.warning("Please enter at least one ingredient.")
        else:
            norm = normalise_list(raw)
            translated = [f"{o}→{n}" for o,n in zip(raw,norm) if o.lower()!=n]
            if translated:
                st.info(f"🔄 Translated: {', '.join(translated)}")

            with st.spinner("🔎 Searching …"):
                fetched = search_recipes(
                    ingredients=norm, cuisine=cuisine, diet=diet,
                    meal_type=meal_type,
                    max_ready_time=TIME_MAP[time_lbl], number=30)

            if fetched:
                with st.spinner("🤖 AI ranking …"):
                    ranked = rank_recipes(fetched, norm)
                st.session_state.recipes          = ranked
                st.session_state.searched         = True
                st.session_state.page             = 0
                st.session_state.last_ingredients = norm

                # save to history (last 8)
                entry = ", ".join(raw)
                hist  = st.session_state.search_history
                if entry not in hist:
                    hist.insert(0, entry)
                    st.session_state.search_history = hist[:8]

                st.success(f"✅ Found {len(ranked)} recipes ranked by AI match score")
            else:
                st.session_state.recipes  = []
                st.session_state.searched = True
                st.error("😕 No recipes found. Try different ingredients or remove filters.")

    # ── Search history ────────────────────────────────────────────
    if st.session_state.search_history:
        with st.expander("🕐 Recent searches"):
            hcols = st.columns(4)
            for i,h in enumerate(st.session_state.search_history):
                with hcols[i%4]:
                    if st.button(h, key=f"hist_{i}"):
                        st.session_state["_prefill"] = h
                        st.rerun()

    # ── Results ───────────────────────────────────────────────────
    if st.session_state.searched and st.session_state.recipes:
        recipes  = st.session_state.recipes
        page     = st.session_state.page
        start    = page * PAGE_SIZE
        end      = start + PAGE_SIZE
        page_rec = recipes[start:end]

        # Stats row
        avg_score = sum(r.get("ai_score",0) for r in recipes)/len(recipes)
        avg_time  = sum(r.get("readyInMinutes",0) or 0 for r in recipes)/len(recipes)
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Recipes Found", len(recipes))
        m2.metric("Showing",       f"{start+1}–{min(end,len(recipes))}")
        m3.metric("Avg AI Score", f"{avg_score:.0f}")
        m4.metric("Avg Cook Time", f"{avg_time:.0f} min")

        st.markdown("<hr style='border-color:rgba(0,0,0,0.08);margin:1.2rem 0'>",
                    unsafe_allow_html=True)
        st.markdown('<p class="section-title">✨ Top Matches</p>', unsafe_allow_html=True)

        # Card grid
        gcols = st.columns(3, gap="medium")
        for i, rec in enumerate(page_rec):
            with gcols[i%3]:
                render_recipe_card(rec, start+i)
                st.markdown("<br>", unsafe_allow_html=True)

        # Pagination
        pc1,pc2,pc3 = st.columns([1,2,1])
        with pc1:
            if page > 0:
                if st.button("← Previous"):
                    st.session_state.page -= 1
                    st.rerun()
        with pc2:
            total_pages = (len(recipes)-1)//PAGE_SIZE + 1
            st.markdown(f"<p style='text-align:center;color:var(--muted);font-size:.85rem'>"
                        f"Page {page+1} of {total_pages}</p>", unsafe_allow_html=True)
        with pc3:
            if end < len(recipes):
                if st.button("Next →"):
                    st.session_state.page += 1
                    st.rerun()

# ══════════════════════════════════════════════════════════════════
# TAB 2  —  SAVED RECIPES
# ══════════════════════════════════════════════════════════════════
with tab_saved:
    saved_list = get_saved_recipes()
    if not saved_list:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#6b6760">
          <div style="font-size:3rem;margin-bottom:1rem">🔖</div>
          <p style="font-size:1.05rem;font-weight:600">No saved recipes yet</p>
          <p>Find a recipe you love and tap <strong>Save recipe</strong> to bookmark it here.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="section-title">🔖 Saved Recipes ({len(saved_list)})</p>',
                    unsafe_allow_html=True)
        gcols = st.columns(3, gap="medium")
        for i,rec in enumerate(saved_list):
            with gcols[i%3]:
                render_recipe_card(rec, f"s{i}")
                st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TAB 3  —  AI CHEF CHAT
# ══════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1c1814,#2e2318);border-radius:14px;
    padding:1.4rem 1.8rem;margin-bottom:1.3rem">
      <p style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;
      color:#f0ede8;margin:0 0 .25rem">🤖 ChefBot — AI Cooking Assistant</p>
      <p style="color:#9e9890;font-size:.88rem;margin:0">Ask about substitutions,
      healthier versions, spice levels, meal ideas, nutrition …</p>
    </div>""", unsafe_allow_html=True)

    # Quick suggestion buttons
    scols = st.columns(3)
    for i,s in enumerate(SUGGESTIONS):
        with scols[i%3]:
            if st.button(s, key=f"sg_{i}"):
                st.session_state.chat.append({"role":"user","content":s})
                with st.spinner("ChefBot thinking …"):
                    reply = chat_with_chef(s, st.session_state.chat)
                st.session_state.chat.append({"role":"assistant","content":reply})
                st.rerun()

    st.markdown("<hr style='border-color:rgba(0,0,0,0.08);margin:.8rem 0'>",
                unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.chat:
        if msg["role"]=="user":
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end">'
                f'<div class="cbuser">{msg["content"]}</div></div>',
                unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="cbbot">🤖 {msg["content"]}</div>',
                        unsafe_allow_html=True)

    # Input + clear
    ic1,ic2 = st.columns([5,1])
    with ic1:
        user_in = st.text_input("Ask ChefBot",placeholder="Ask anything about cooking …",
                                label_visibility="collapsed",key="chat_in")
    with ic2:
        if st.button("🗑️ Clear"):
            st.session_state.chat = []; st.rerun()

    if user_in:
        st.session_state.chat.append({"role":"user","content":user_in})
        with st.spinner("ChefBot thinking …"):
            reply = chat_with_chef(user_in, st.session_state.chat)
        st.session_state.chat.append({"role":"assistant","content":reply})
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# TAB 4  —  RANDOM RECIPE
# ══════════════════════════════════════════════════════════════════
with tab_random:
    st.markdown('<p class="section-title">🎲 Feeling adventurous?</p>',
                unsafe_allow_html=True)
    st.markdown("Hit the button to discover a random recipe from a surprise ingredient.")

    if st.button("🎲 Surprise me!", use_container_width=True):
        pick = random.choice(TRENDING)
        st.info(f"🔀 Searching recipes with: **{pick}**")
        with st.spinner("Finding a surprise …"):
            fetched = search_recipes(ingredients=[pick], number=10)
        if fetched:
            ranked = rank_recipes(fetched, [pick])
            rec    = random.choice(ranked[:5]) if ranked else ranked[0]
            render_recipe_card(rec, "rand")
        else:
            st.error("Couldn't find a recipe this time. Try again!")

# ── Footer ───────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:1.3rem;color:#6b6760;font-size:.78rem;
border-top:1px solid rgba(0,0,0,0.08)">
  Built with ❤️ using Streamlit &nbsp;·&nbsp; Powered by Spoonacular API &amp; Google Gemini<br>
  <span style="opacity:.6">RecipeAI — AI-Powered Smart Cooking Assistant</span>
</div>""", unsafe_allow_html=True)
