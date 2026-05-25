# app/gemini_client.py

import os
from google import genai

_client = None


def get_client():
    """
    Lazy initialization for OpenClaw-safe execution.
    Prevents import-time side effects.
    """
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")

        _client = genai.Client(api_key=api_key)

    return _client


def analyze_text(text: str) -> dict:
    client = get_client()

    prompt = f"""
You are a bilingual homework tutor.

Return STRICT JSON ONLY:

{{
  "answer": "...",
  "explanation_en": "...",
  "explanation_zh": "...",
  "topic": "...",
  "difficulty": "easy|medium|hard",
  "common_mistake": "..."
}}

Question:
{text}
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt
    )

    import json
    try:
        return json.loads(response.text)
    except:
        return {
            "answer": "",
            "explanation_en": response.text,
            "explanation_zh": "",
            "topic": "unknown",
            "difficulty": "unknown",
            "common_mistake": "parse_failed"
        }



# def get_client():
#     return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_homework(user, text, image_bytes=None):
    client = get_client()

    prompt = f"""
You are a strict but friendly homework tutor.

Student: {user}

Task:
- Solve the problem
- Explain in English and Chinese
- Be concise
"""

    contents = [prompt]

    # text input
    if text:
        contents.append(text)

    # image input (FIXED VERSION)
    if image_bytes:
        contents.append(
            {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
        )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=contents
    )

    return {
        "answer": response.text
    }