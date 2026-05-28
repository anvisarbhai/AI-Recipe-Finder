"""
components/recipe_card.py
─────────────────────────────────────────────────────────────────
Renders one recipe card and its expanded detail view.
─────────────────────────────────────────────────────────────────
"""
import streamlit as st
from database import save_recipe, remove_recipe, is_saved
import plotly.graph_objects as go


def _score_bar(score: float) -> str:
    pct = int(score * 100)
    return f"""
    <div class="score-bar-wrap">
      <span class="score-label">AI Match Score &nbsp; {pct}%</span>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width:{pct}%"></div>
      </div>
    </div>"""


def _nutrition_mini(recipe: dict) -> dict:
    """Extract calorie/protein/carbs/fat from the Spoonacular nutrition blob."""
    result = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    try:
        nutrients = recipe["nutrition"]["nutrients"]
        mapping = {
            "Calories":      "calories",
            "Protein":       "protein",
            "Carbohydrates": "carbs",
            "Fat":           "fat",
        }
        for n in nutrients:
            key = mapping.get(n["name"])
            if key:
                result[key] = round(n["amount"])
    except (KeyError, TypeError):
        pass
    return result


def render_recipe_card(recipe: dict, index: int) -> None:
    """
    Render a glassmorphism-style recipe card inside a Streamlit column.
    `index` is used to create unique widget keys.
    """
    rid    = recipe.get("id", index)
    title  = recipe.get("title", "Unknown Recipe")
    image  = recipe.get("image", "")
    time   = recipe.get("readyInMinutes", "?")
    score  = recipe.get("ai_score", 0)
    health = recipe.get("healthScore", 0)
    likes  = recipe.get("aggregateLikes", 0)
    missing = recipe.get("missing_items", [])
    saved  = is_saved(rid)

    # ── Card header ──────────────────────────────────────────────
    img_html = f'<img class="recipe-img" src="{image}" alt="{title}" />' if image else \
               '<div style="height:200px;background:linear-gradient(135deg,#e85d26,#f5a623);display:flex;align-items:center;justify-content:center;font-size:3rem;">🍽️</div>'

    missing_html = ""
    if missing:
        items = ", ".join(missing[:4])
        more  = f" +{len(missing)-4} more" if len(missing) > 4 else ""
        missing_html = f'<div class="missing-box">🛒 <strong>Still need:</strong> {items}{more}</div>'

    saved_badge = '<span class="saved-badge">✓ Saved</span>' if saved else ""

    card_html = f"""
    <div class="recipe-card">
      {img_html}
      <div class="recipe-body">
        <p class="recipe-title">{title} {saved_badge}</p>
        <div class="recipe-meta">
          <span class="pill">⏱ {time} min</span>
          <span class="pill">❤️ {likes}</span>
          <span class="pill-accent">🌿 {health} health</span>
        </div>
        {_score_bar(score)}
        {missing_html}
      </div>
    </div>"""

    st.markdown(card_html, unsafe_allow_html=True)

    # ── Expand for full details ───────────────────────────────────
    with st.expander("📖 View full recipe"):
        _render_details(recipe, index)


def _render_details(recipe: dict, index: int) -> None:
    """Full recipe details: ingredients, instructions, nutrition chart."""
    rid   = recipe.get("id", index)
    title = recipe.get("title", "")
    saved = is_saved(rid)

    # Save / unsave button
    col_save, col_share = st.columns([1, 1])
    with col_save:
        label = "🗑️ Remove bookmark" if saved else "🔖 Save recipe"
        if st.button(label, key=f"save_{rid}_{index}"):
            if saved:
                remove_recipe(rid)
                st.toast("Removed from saved recipes", icon="🗑️")
            else:
                save_recipe(recipe)
                st.toast("Recipe saved!", icon="✅")
            st.rerun()
    with col_share:
        share_url = f"https://spoonacular.com/recipes/{title.lower().replace(' ','-')}-{rid}"
        st.link_button("🔗 View on Spoonacular", share_url)

    # Ingredients
    all_ingredients = (
        recipe.get("extendedIngredients")
        or recipe.get("usedIngredients", []) + recipe.get("missedIngredients", [])
    )
    if all_ingredients:
        st.markdown("**🥕 Ingredients**")
        cols = st.columns(2)
        for i, ing in enumerate(all_ingredients):
            name   = ing.get("original") or ing.get("name", "")
            amount = ing.get("amount", "")
            unit   = ing.get("unit", "")
            with cols[i % 2]:
                st.markdown(f"• {name}")

    # Instructions
    instructions = recipe.get("analyzedInstructions", [])
    if instructions:
        st.markdown("**📝 Instructions**")
        for step in instructions[0].get("steps", []):
            n = step.get("number", "")
            s = step.get("step", "")
            st.markdown(f"**{n}.** {s}")
    elif recipe.get("instructions"):
        st.markdown("**📝 Instructions**")
        st.markdown(recipe["instructions"], unsafe_allow_html=True)

    # Nutrition chart
    nutr = _nutrition_mini(recipe)
    if any(nutr.values()):
        st.markdown("**📊 Nutrition per serving**")
        _nutrition_chart(nutr, recipe.get("id", index))


def _nutrition_chart(nutr: dict, key: int) -> None:
    labels  = ["Protein", "Carbohydrates", "Fat"]
    values  = [nutr["protein"], nutr["carbs"], nutr["fat"]]
    colors  = ["#e85d26", "#f5a623", "#fbbf24"]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.5,
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textfont=dict(size=13),
    )])
    fig.update_layout(
        showlegend=True, height=260, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=12)),
        annotations=[dict(text=f"{nutr['calories']}<br>kcal",
                          x=0.5, y=0.5, font_size=14, showarrow=False)],
    )
    st.plotly_chart(fig, use_container_width=True, key=f"pie_{key}")
