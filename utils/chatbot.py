"""
utils/chatbot.py
─────────────────────────────────────────────────────────────────
Wraps the Google Gemini API to power the AI Cooking Assistant.
Falls back gracefully if the key is missing or quota is exceeded.
─────────────────────────────────────────────────────────────────
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _get_gemini_key() -> str:
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")


def chat_with_chef(user_message: str, conversation_history: list[dict]) -> str:
    """
    Send a message to Gemini and return the assistant reply as a string.
    conversation_history is a list of {"role": "user"/"assistant", "content": "..."}.
    """
    api_key = _get_gemini_key()
    if not api_key:
        return (
            "🔑 Gemini API key not found. Add GEMINI_API_KEY to your .env file "
            "or Streamlit Secrets to enable the AI chef."
        )

    try:
        import google.generativeai as genai  # lazy import

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=(
                "You are ChefBot, a warm and knowledgeable AI cooking assistant. "
                "You help users with ingredient substitutions, healthier alternatives, "
                "cooking tips, spice levels, meal suggestions, and nutritional advice. "
                "Keep answers concise, friendly, and practical. Use food emojis sparingly."
            ),
        )

        # Build Gemini-format history
        gemini_history = []
        for msg in conversation_history[:-1]:  # exclude the latest user message
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_message)
        return response.text

    except ImportError:
        return "📦 google-generativeai package not installed. Run: pip install google-generativeai"
    except Exception as e:
        return f"⚠️ ChefBot error: {e}"
