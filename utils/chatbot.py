"""
utils/chatbot.py  —  Gemini AI Chef (fixed for latest SDK)
Uses gemini-2.0-flash which is available on all free API keys.
"""
import os, streamlit as st


SYSTEM_PROMPT = (
    "You are ChefBot, a warm and expert AI cooking assistant. "
    "Help users with ingredient substitutions, healthier alternatives, "
    "cooking tips, spice adjustments, meal suggestions, and nutrition. "
    "Keep replies concise, practical, and friendly. Use food emojis sparingly."
)

def _gemini_key() -> str:
    
    try:
        k = st.secrets.get("GEMINI_API_KEY","")
        if k and k != "your_gemini_api_key_here":
            return k
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY","")

def chat_with_chef(user_message: str, history: list) -> str:
    api_key = _gemini_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return "🔑 Gemini API key not configured. Add GEMINI_API_KEY to your .env file."

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        # Build history in Gemini format (exclude last user message)
        gem_history = []
        for msg in history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gem_history.append({"role": role, "parts": [msg["content"]]})

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        chat  = model.start_chat(history=gem_history)
        resp  = chat.send_message(user_message)
        return resp.text

    except Exception as e:
        err = str(e)
        if "404" in err or "not found" in err.lower():
            return "⚠️ Gemini model unavailable. Try regenerating your API key at aistudio.google.com."
        if "quota" in err.lower() or "429" in err:
            return "⏳ Gemini rate limit reached. Please wait a moment and try again."
        return f"⚠️ ChefBot error: {err}"
