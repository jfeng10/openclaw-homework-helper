from app.gemini_client import analyze_homework
from app.db import log_homework
from app.telegram_utils import download_telegram_image
import os
from app.db import init_db
init_db()


def run(event):
    user = event.get("user", "unknown")
    text = event.get("text", "")

    photo = event.get("photo")
    image_bytes = None

    if photo:
        file_id = photo[-1]["file_id"] if isinstance(photo, list) else photo

        image_bytes = download_telegram_image(
            file_id,
            os.getenv("TELEGRAM_BOT_TOKEN")
        )

    from app.gemini_client import analyze_homework
    from app.db import log_homework

    result = analyze_homework(
        user=user,
        text=text,
        image_bytes=image_bytes
    )

    log_homework(user, text, result)

    return result

def extract_image(event):
    """
    OpenClaw/Telegram adapters vary.
    We normalize all cases here.
    """

    # Case 1: direct URL
    if "image_url" in event:
        return event["image_url"]

    # Case 2: file_id (Telegram style)
    if "photo" in event:
        photos = event["photo"]
        if isinstance(photos, list) and len(photos) > 0:
            return photos[-1]  # highest resolution

    return None


def format_reply(result):
    return {
        "answer": result.get("answer", ""),
        "explanation_en": result.get("explanation_en", ""),
        "explanation_zh": result.get("explanation_zh", "")
    }