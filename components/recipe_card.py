"""
components/recipe_card.py  —  Recipe card + detail expander
"""
import streamlit as st
import plotly.graph_objects as go
from database import save_recipe, remove_recipe, is_saved

def _nutr(recipe):
    r = {"calories":0,"protein":0,"carbs":0,"fat":0}
    try:
        for n in recipe["nutrition"]["nutrients"]:
            if n["name"]=="Calories":      r["calories"]=round(n["amount"])
            elif n["name"]=="Protein":     r["protein"]=round(n["amount"])
            elif n["name"]=="Carbohydrates":r["carbs"]=round(n["amount"])
            elif n["name"]=="Fat":         r["fat"]=round(n["amount"])
    except Exception:
        pass
    return r

def render_recipe_card(recipe: dict, index) -> None:
    rid    = recipe.get("id", index)
    title  = recipe.get("title","Unknown")
    image  = recipe.get("image","")
    time   = recipe.get("readyInMinutes","?")
    health = recipe.get("healthScore",0) or 0
    likes  = recipe.get("aggregateLikes",0) or 0
    score  = recipe.get("ai_score",0)
    pct    = recipe.get("match_pct",0)
    missing= recipe.get("missing_items",[])
    saved  = is_saved(rid)

    img_html = (f'<img class="rcard-img" src="{image}" alt="{title}"/>' if image else
                '<div style="height:195px;background:linear-gradient(135deg,#e85d26,#f5a623);'
                'display:flex;align-items:center;justify-content:center;font-size:3rem">🍽️</div>')

    miss_html = ""
    if missing:
        items = ", ".join(missing[:4])
        more  = f" +{len(missing)-4} more" if len(missing)>4 else ""
        miss_html = f'<div class="missing">🛒 <strong>Still need:</strong> {items}{more}</div>'

    saved_pill = '<span class="pill-green">✓ Saved</span>' if saved else ""

    st.markdown(f"""
    <div class="rcard">
      {img_html}
      <div class="rcard-body">
        <p class="rcard-title">{title} {saved_pill}</p>
        <div class="rcard-meta">
          <span class="pill">⏱ {time} min</span>
          <span class="pill">❤️ {likes}</span>
          <span class="pill-hot">🌿 {health}% health</span>
        </div>
        <div class="mbar-wrap">
          <span class="mbar-label">Ingredient match &nbsp;{pct}%</span>
          <div class="mbar-bg"><div class="mbar-fill" style="width:{pct}%"></div></div>
        </div>
        {miss_html}
      </div>
    </div>""", unsafe_allow_html=True)

    with st.expander("📖 Full recipe"):
        _detail(recipe, index)

def _detail(recipe, index):
    rid   = recipe.get("id", index)
    title = recipe.get("title","")
    saved = is_saved(rid)

    c1, c2 = st.columns(2)
    with c1:
        lbl = "🗑️ Remove" if saved else "🔖 Save recipe"
        if st.button(lbl, key=f"sv_{rid}_{index}"):
            if saved: remove_recipe(rid); st.toast("Removed", icon="🗑️")
            else:     save_recipe(recipe); st.toast("Saved!", icon="✅")
            st.rerun()
    with c2:
        url = f"https://spoonacular.com/recipes/{title.lower().replace(' ','-')}-{rid}"
        st.link_button("🔗 Spoonacular", url)

    # Cuisines / diets
    cuisines = recipe.get("cuisines",[])
    diets    = recipe.get("diets",[])
    if cuisines or diets:
        tags = " ".join(f'<span class="pill">{t}</span>' for t in cuisines+diets[:3])
        st.markdown(tags, unsafe_allow_html=True)

    # Why this recipe
    used   = recipe.get("usedIngredients",[])
    missed = recipe.get("missedIngredients",[])
    if used:
        u_names = ", ".join(i.get("name","") for i in used)
        st.success(f"✅ **Matches your ingredients:** {u_names}")
    if missed:
        m_names = ", ".join(i.get("name","") for i in missed[:5])
        st.info(f"🛒 **You'd also need:** {m_names}")

    # Ingredients list
    ings = recipe.get("extendedIngredients") or used+missed
    if ings:
        st.markdown("**🥕 Ingredients**")
        cols = st.columns(2)
        for i,ing in enumerate(ings):
            txt = ing.get("original") or ing.get("name","")
            with cols[i%2]: st.markdown(f"• {txt}")

    # Instructions
    steps = recipe.get("analyzedInstructions",[])
    if steps:
        st.markdown("**📝 Instructions**")
        for s in steps[0].get("steps",[]):
            st.markdown(f"**{s.get('number','')}.**  {s.get('step','')}")
    elif recipe.get("instructions"):
        st.markdown("**📝 Instructions**")
        st.markdown(recipe["instructions"], unsafe_allow_html=True)

    # Nutrition chart
    n = _nutr(recipe)
    if any(n.values()):
        st.markdown("**📊 Nutrition per serving**")
        fig = go.Figure(go.Pie(
            labels=["Protein","Carbs","Fat"],
            values=[n["protein"],n["carbs"],n["fat"]],
            hole=.5,
            marker=dict(colors=["#e85d26","#f5a623","#fbbf24"],
                        line=dict(color="#fff",width=2)),
        ))
        fig.update_layout(
            height=240, margin=dict(t=8,b=8,l=8,r=8),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text=f"{n['calories']}<br>kcal",x=.5,y=.5,
                              font_size=13,showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True, key=f"pie_{rid}_{index}")
