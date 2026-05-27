# app/gemini_client.py

import json
import logging
import os

logger = logging.getLogger(__name__)
_client = None
GEMINI_FLASH_MODEL = "gemini-3.1-flash-lite-preview"
GEMINI_PRO_MODEL = "gemini-3.1-pro-preview"


def _coerce_response_text(response):
    return getattr(response, "text", "") or ""


def get_client():
    """
    Lazy initialization for OpenClaw-safe execution.
    Prevents import-time side effects.
    """
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logger.error("Gemini client initialization failed: GEMINI_API_KEY not set")
            raise ValueError("GEMINI_API_KEY not set")

        from google import genai

        logger.info("Initializing Gemini client")
        _client = genai.Client(api_key=api_key)
    else:
        logger.debug("Reusing Gemini client")

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

    logger.info(
        "Calling Gemini for text homework analysis",
        extra={"model": GEMINI_FLASH_MODEL, "text_length": len(text or "")},
    )
    response = client.models.generate_content(
        model=GEMINI_FLASH_MODEL,
        contents=prompt
    )
    response_text = _coerce_response_text(response)

    try:
        parsed = json.loads(response_text)
        logger.debug("Gemini text response parsed as JSON")
        return parsed
    except Exception:
        logger.exception("Failed to parse Gemini text response as JSON")
        return {
            "answer": "",
            "explanation_en": response_text,
            "explanation_zh": "",
            "topic": "unknown",
            "difficulty": "unknown",
            "common_mistake": "parse_failed"
        }

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

    logger.info(
        "Calling Gemini for homework assessment",
        extra={
            "model": GEMINI_FLASH_MODEL,
            "user": user,
            "text_length": len(text or ""),
            "has_image": image_bytes is not None,
            "image_bytes": len(image_bytes or b""),
        },
    )
    response = client.models.generate_content(
        model=GEMINI_FLASH_MODEL,
        contents=contents
    )

    response_text = _coerce_response_text(response)
    logger.info(
        "Gemini homework assessment complete",
        extra={"response_length": len(response_text), "user": user},
    )
    return {
        "answer": response_text
    }
