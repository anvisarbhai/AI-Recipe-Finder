"""
styles/main_css.py
─────────────────────────────────────────────────────────────────
All custom CSS injected into Streamlit via st.markdown.
Edit colours/fonts here to retheme the whole app in one place.
─────────────────────────────────────────────────────────────────
"""

MAIN_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── CSS Variables (Light & Dark) ───────────────────────────── */
:root {
  --bg:          #faf9f7;
  --surface:     #ffffff;
  --surface2:    #f3f1ed;
  --border:      rgba(0,0,0,0.08);
  --text:        #1a1814;
  --text-muted:  #6b6760;
  --accent:      #e85d26;
  --accent2:     #f5a623;
  --accent-glow: rgba(232,93,38,0.18);
  --card-shadow: 0 2px 20px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04);
  --radius:      16px;
  --font-head:   'Syne', sans-serif;
  --font-body:   'DM Sans', sans-serif;
}

[data-theme="dark"], .dark-mode {
  --bg:          #121110;
  --surface:     #1e1c1a;
  --surface2:    #272422;
  --border:      rgba(255,255,255,0.08);
  --text:        #f0ede8;
  --text-muted:  #9e9890;
  --card-shadow: 0 2px 20px rgba(0,0,0,0.4), 0 1px 4px rgba(0,0,0,0.2);
}

/* ── Global reset ───────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: var(--font-body) !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

/* ── Streamlit chrome cleanup ───────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1200px !important; }

/* ── Hero Section ───────────────────────────────────────────── */
.hero {
  background: linear-gradient(135deg, #1a1814 0%, #2d2520 50%, #1a1814 100%);
  border-radius: var(--radius);
  padding: 4rem 3rem 3.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 70% 50%, rgba(232,93,38,0.25) 0%, transparent 60%);
}
.hero-title {
  font-family: var(--font-head) !important;
  font-size: clamp(2.2rem, 5vw, 3.8rem) !important;
  font-weight: 800 !important;
  line-height: 1.1 !important;
  color: #f0ede8 !important;
  margin: 0 0 0.6rem 0 !important;
  position: relative;
}
.hero-title span {
  background: linear-gradient(90deg, #e85d26, #f5a623);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  color: #9e9890 !important;
  font-size: 1.1rem !important;
  font-weight: 300 !important;
  margin: 0 !important;
  position: relative;
}
.hero-badge {
  display: inline-block;
  background: rgba(232,93,38,0.15);
  border: 1px solid rgba(232,93,38,0.3);
  color: #e85d26;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 0.3rem 0.9rem;
  border-radius: 100px;
  margin-bottom: 1.2rem;
  position: relative;
}

/* ── Section headings ───────────────────────────────────────── */
.section-title {
  font-family: var(--font-head) !important;
  font-size: 1.5rem !important;
  font-weight: 700 !important;
  margin-bottom: 1rem !important;
  color: var(--text) !important;
}

/* ── Search Panel ───────────────────────────────────────────── */
.search-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.8rem 2rem;
  box-shadow: var(--card-shadow);
  margin-bottom: 2rem;
}

/* ── Recipe Card ────────────────────────────────────────────── */
.recipe-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--card-shadow);
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  height: 100%;
}
.recipe-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
}
.recipe-img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}
.recipe-body {
  padding: 1.1rem 1.2rem 1.2rem;
}
.recipe-title {
  font-family: var(--font-head) !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  margin: 0 0 0.6rem 0 !important;
  line-height: 1.3 !important;
  color: var(--text) !important;
}
.recipe-meta {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}
.pill {
  background: var(--surface2);
  border-radius: 100px;
  padding: 0.2rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
  white-space: nowrap;
}
.pill-accent {
  background: var(--accent-glow);
  color: var(--accent);
  border-radius: 100px;
  padding: 0.2rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
}
.missing-box {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 10px;
  padding: 0.6rem 0.8rem;
  margin: 0.6rem 0;
  font-size: 0.82rem;
  color: #9a3412;
}
.missing-box strong { color: #c2410c; }

/* ── Score bar ──────────────────────────────────────────────── */
.score-bar-wrap { margin: 0.5rem 0 0.8rem; }
.score-label {
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.05em;
  text-transform: uppercase; color: var(--text-muted);
}
.score-bar-bg {
  background: var(--surface2); border-radius: 100px; height: 6px;
  overflow: hidden; margin-top: 4px;
}
.score-bar-fill {
  background: linear-gradient(90deg, #e85d26, #f5a623);
  height: 100%; border-radius: 100px;
  transition: width 0.6s ease;
}

/* ── Buttons ────────────────────────────────────────────────── */
.stButton > button {
  font-family: var(--font-body) !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  transition: all 0.18s ease !important;
  border: none !important;
}
.stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }
div[data-testid="stForm"] .stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #e85d26, #f5a623) !important;
  color: white !important;
  padding: 0.65rem 2rem !important;
}

/* ── Chatbot ─────────────────────────────────────────────────── */
.chat-bubble-user {
  background: linear-gradient(135deg, #e85d26, #f5a623);
  color: white; border-radius: 18px 18px 4px 18px;
  padding: 0.7rem 1rem; margin: 0.4rem 0; max-width: 78%;
  margin-left: auto; font-size: 0.92rem;
}
.chat-bubble-bot {
  background: var(--surface2);
  color: var(--text); border-radius: 18px 18px 18px 4px;
  padding: 0.7rem 1rem; margin: 0.4rem 0; max-width: 78%;
  font-size: 0.92rem; border: 1px solid var(--border);
}
.chat-container {
  max-height: 420px; overflow-y: auto;
  padding: 0.5rem; margin-bottom: 1rem;
}

/* ── Nutrition card ─────────────────────────────────────────── */
.nutrition-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem;
  text-align: center;
  box-shadow: var(--card-shadow);
}
.nutrition-value {
  font-family: var(--font-head) !important;
  font-size: 1.9rem !important; font-weight: 800 !important;
  background: linear-gradient(135deg, #e85d26, #f5a623);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.nutrition-label {
  font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--text-muted);
}

/* ── Saved badge ────────────────────────────────────────────── */
.saved-badge {
  background: #dcfce7; color: #15803d;
  border-radius: 100px; padding: 0.15rem 0.6rem;
  font-size: 0.72rem; font-weight: 600;
}

/* ── Streamlit overrides ────────────────────────────────────── */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
.stTextInput input, .stMultiSelect [data-baseweb], .stSelectbox [data-baseweb] {
  border-radius: 10px !important;
}
div[data-testid="stTabs"] button {
  font-family: var(--font-head) !important;
  font-weight: 600 !important;
}
</style>
"""
