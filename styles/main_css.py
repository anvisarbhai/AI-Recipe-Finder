"""
styles/main_css.py  —  Clean light-only professional theme
Dark mode completely removed.
"""

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

/* ── Variables ── */
:root {
  --bg:       #f8f6f2;
  --surface:  #ffffff;
  --surface2: #f0ede8;
  --border:   rgba(0,0,0,0.09);
  --text:     #1a1814;
  --muted:    #6b6760;
  --accent:   #e85d26;
  --accent2:  #f5a623;
  --glow:     rgba(232,93,38,0.14);
  --shadow:   0 2px 20px rgba(0,0,0,0.07),0 1px 4px rgba(0,0,0,0.04);
  --r:        14px;
  --fh:       'Syne',sans-serif;
  --fb:       'DM Sans',sans-serif;
}

/* ── Global ── */
html,body,[class*="css"]{font-family:var(--fb)!important;background:var(--bg)!important;color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1.2rem!important;max-width:1180px!important;}

/* ── Hero ── */
.hero{background:linear-gradient(135deg,#1c1814 0%,#2e2318 55%,#1c1814 100%);
  border-radius:var(--r);padding:3.8rem 3rem 3.2rem;margin-bottom:1.8rem;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 75% 50%,rgba(232,93,38,0.22) 0%,transparent 62%);}
.hero-badge{display:inline-block;background:rgba(232,93,38,0.15);border:1px solid rgba(232,93,38,0.32);
  color:#e85d26;font-size:.72rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  padding:.28rem .9rem;border-radius:100px;margin-bottom:1.1rem;position:relative;}
.hero-title{font-family:var(--fh)!important;font-size:clamp(2rem,4.5vw,3.5rem)!important;
  font-weight:800!important;line-height:1.1!important;color:#f0ede8!important;
  margin:0 0 .55rem!important;position:relative;}
.hero-title span{background:linear-gradient(90deg,#e85d26,#f5a623);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.hero-sub{color:#9e9890!important;font-size:1rem!important;font-weight:300!important;
  margin:0!important;position:relative;max-width:560px;}

/* ── Search panel ── */
.search-panel{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  padding:1.6rem 1.8rem;box-shadow:var(--shadow);margin-bottom:1.6rem;}

/* ── Section title ── */
.section-title{font-family:var(--fh)!important;font-size:1.35rem!important;
  font-weight:700!important;margin-bottom:.9rem!important;color:var(--text)!important;}

/* ── Recipe card ── */
.rcard{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  overflow:hidden;box-shadow:var(--shadow);transition:transform .22s ease,box-shadow .22s ease;height:100%;}
.rcard:hover{transform:translateY(-4px);
  box-shadow:0 14px 40px rgba(0,0,0,0.11),0 2px 8px rgba(0,0,0,0.05);}
.rcard-img{width:100%;height:195px;object-fit:cover;}
.rcard-body{padding:1rem 1.1rem 1.15rem;}
.rcard-title{font-family:var(--fh)!important;font-size:1rem!important;font-weight:700!important;
  margin:0 0 .55rem!important;line-height:1.3!important;color:var(--text)!important;}
.rcard-meta{display:flex;gap:.45rem;flex-wrap:wrap;margin-bottom:.65rem;}
.pill{background:var(--surface2);border-radius:100px;padding:.18rem .62rem;
  font-size:.72rem;font-weight:500;color:var(--muted);}
.pill-hot{background:var(--glow);color:var(--accent);border-radius:100px;
  padding:.18rem .62rem;font-size:.72rem;font-weight:700;}
.pill-green{background:#dcfce7;color:#15803d;border-radius:100px;
  padding:.18rem .62rem;font-size:.72rem;font-weight:600;}

/* ── Match bar ── */
.mbar-wrap{margin:.4rem 0 .7rem;}
.mbar-label{font-size:.7rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);}
.mbar-bg{background:var(--surface2);border-radius:100px;height:5px;overflow:hidden;margin-top:3px;}
.mbar-fill{background:linear-gradient(90deg,#e85d26,#f5a623);height:100%;border-radius:100px;}

/* ── Missing box ── */
.missing{background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;
  padding:.55rem .75rem;margin:.5rem 0;font-size:.8rem;color:#9a3412;}
.missing strong{color:#c2410c;}

/* ── Buttons ── */
.stButton>button{font-family:var(--fb)!important;font-weight:600!important;
  border-radius:10px!important;border:none!important;transition:all .18s ease!important;}
.stButton>button:hover{opacity:.86;transform:translateY(-1px);}
div[data-testid="stForm"] .stButton>button[kind="primary"]{
  background:linear-gradient(135deg,#e85d26,#f5a623)!important;
  color:white!important;padding:.6rem 1.8rem!important;}

/* ── Chat ── */
.cbuser{background:linear-gradient(135deg,#e85d26,#f5a623);color:white;
  border-radius:18px 18px 4px 18px;padding:.65rem .95rem;margin:.35rem 0;
  max-width:76%;margin-left:auto;font-size:.9rem;}
.cbbot{background:var(--surface2);color:var(--text);border:1px solid var(--border);
  border-radius:18px 18px 18px 4px;padding:.65rem .95rem;margin:.35rem 0;
  max-width:76%;font-size:.9rem;}

/* ── Nutrition card ── */
.ncard{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  padding:1.2rem;text-align:center;box-shadow:var(--shadow);}
.nval{font-family:var(--fh)!important;font-size:1.8rem!important;font-weight:800!important;
  background:linear-gradient(135deg,#e85d26,#f5a623);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.nlabel{font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);}

/* ── Streamlit tweaks ── */
[data-testid="stExpander"]{border:1px solid var(--border)!important;border-radius:12px!important;}
.stTextInput input,.stSelectbox [data-baseweb]{border-radius:10px!important;}
div[data-testid="stTabs"] button{font-family:var(--fh)!important;font-weight:600!important;}
div[data-testid="metric-container"]{background:var(--surface);border:1px solid var(--border);
  border-radius:12px;padding:.8rem 1rem;box-shadow:var(--shadow);}
</style>
"""
