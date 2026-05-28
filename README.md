# 🍳 RecipeAI — AI-Powered Recipe Finder & Smart Cooking Assistant

A production-ready, portfolio-worthy web app that finds recipes from your
fridge ingredients, ranks them with an AI engine, shows missing ingredients,
and lets you chat with an AI chef.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔍 Smart Search | Filter by cuisine, diet, meal type, cooking time |
| 🤖 AI Ranking | TF-IDF + cosine similarity + weighted scoring |
| 🗺️ Ingredient Normalisation | capsicum→bell pepper, paneer→cottage cheese … |
| 🛒 Missing Ingredients | "You only need basil and pasta to make this" |
| 📊 Nutrition Charts | Interactive Plotly pie charts per recipe |
| 🔖 Save Recipes | SQLite bookmarks, persisted across sessions |
| 🌙 Dark Mode | One-click toggle |
| 🤖 AI Chef Chat | Google Gemini-powered cooking assistant |
| 📱 Mobile Responsive | Looks great on any screen size |

---

## 🚀 Quick Start (Local)

### Step 1 — Prerequisites
- Python 3.10 or newer
- A free [Spoonacular API key](https://spoonacular.com/food-api)
- (Optional) A free [Google Gemini API key](https://aistudio.google.com/)

### Step 2 — Clone / create the project folder

```bash
# If you cloned from GitHub:
git clone https://github.com/YOUR_USERNAME/recipe-ai.git
cd recipe-ai

# Or just cd into wherever you saved the project:
cd recipe-ai
```

### Step 3 — Create a virtual environment (strongly recommended)

```bash
python -m venv venv

# Activate it:
# macOS / Linux:
source venv/bin/activate
# Windows CMD:
venv\Scripts\activate
# Windows PowerShell:
venv\Scripts\Activate.ps1
```

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Add your API keys

Open `.env` and replace the placeholder values:

```
SPOONACULAR_API_KEY=abc123yourkey
GEMINI_API_KEY=AIzaSy...yourkey
```

### Step 6 — Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser. 🎉

---

## 🌐 Deploy to Streamlit Community Cloud (FREE)

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/recipe-ai.git
git push -u origin main
```

> ⚠️ Make sure `.env` and `.streamlit/secrets.toml` are in `.gitignore`
> (they are by default in this project).

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repository, branch `main`, file `app.py`
5. Click **Advanced settings → Secrets** and paste:

```toml
SPOONACULAR_API_KEY = "your_key_here"
GEMINI_API_KEY      = "your_key_here"
```

6. Click **Deploy**
7. Your live URL will be `https://YOUR_APP.streamlit.app` ✅

---

## 📁 Project Structure

```
recipe-ai/
├── app.py                  ← Main Streamlit app (entry point)
├── requirements.txt        ← Python dependencies
├── .env                    ← Local API keys (never commit!)
├── .gitignore
│
├── .streamlit/
│   ├── config.toml         ← Theme and server settings
│   └── secrets.toml        ← Cloud secrets (never commit!)
│
├── styles/
│   └── main_css.py         ← All custom CSS (glassmorphism, dark mode …)
│
├── components/
│   └── recipe_card.py      ← Recipe card UI + nutrition chart
│
├── utils/
│   ├── api.py              ← Spoonacular API wrapper
│   └── chatbot.py          ← Gemini AI chef wrapper
│
├── models/
│   └── recommender.py      ← TF-IDF + cosine similarity engine
│
└── database/
    └── db.py               ← SQLite bookmark persistence
```

---

## 🔧 Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `402 Payment Required` | Spoonacular quota exceeded | Wait 24h or upgrade plan |
| `401 Unauthorized` | Wrong API key | Check `.env` spelling |
| `ModuleNotFoundError` | Missing package | `pip install -r requirements.txt` |
| Blank page on deploy | Missing secrets | Add keys in Streamlit Cloud secrets panel |
| `sqlite3.OperationalError` | DB path issue | The DB auto-creates; check write permissions |

---

## 🔮 Future Enhancements

- 📸 **Fridge image detection** — upload a photo, YOLO/Gemini Vision detects ingredients
- 📅 **Weekly meal planner** — drag-and-drop calendar
- 🛍️ **Grocery list generator** — export missing ingredients to PDF
- 👤 **User accounts** — login with Google, personal bookmarks
- 🌍 **Recipe sharing** — public profile with your favourites
- 🔔 **Notifications** — "You have ingredients expiring soon — make this!"

---

## 📄 License

MIT — free to use, modify, and deploy.
