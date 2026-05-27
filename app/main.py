import logging
import os

from app.db import init_db, log_homework
from app.gemini_client import analyze_homework
from app.telegram_utils import download_telegram_image

logger = logging.getLogger(__name__)


def run(event):
    logger.info(
        "Homework workflow invoked",
        extra={
            "event_keys": sorted(event.keys()),
            "has_photo": bool(event.get("photo")),
            "has_image_path": bool(event.get("image_path")),
            "has_image_bytes": bool(event.get("image_bytes")),
        },
    )

    try:
        init_db()
        user = event.get("user", "unknown")
        text = event.get("text", "") or event.get("caption", "") or ""
        image_bytes = _load_image_bytes(event)

        result = analyze_homework(
            user=user,
            text=text,
            image_bytes=image_bytes
        )

        row_id = log_homework(user, text, result)
        result.setdefault("metadata", {})
        result["metadata"].update(
            {
                "sqlite_row_id": row_id,
                "workflow": "app.main.run",
                "persisted": True,
            }
        )
        logger.info(
            "Homework workflow completed",
            extra={"sqlite_row_id": row_id, "has_image": image_bytes is not None},
        )
        return result
    except Exception as exc:
        logger.exception("Homework workflow failed")
        return {
            "error": str(exc),
            "metadata": {
                "workflow": "app.main.run",
                "persisted": False,
            },
        }


def _load_image_bytes(event):
    if event.get("image_bytes"):
        logger.info("Using image bytes supplied directly to workflow")
        return event["image_bytes"]

    image_path = event.get("image_path")
    if image_path:
        logger.info("Reading homework image from local path")
        with open(image_path, "rb") as image_file:
            data = image_file.read()
        logger.info("Local homework image loaded", extra={"image_bytes": len(data)})
        return data

    photo = event.get("photo")
    if photo:
        file_id = _extract_telegram_file_id(photo)
        logger.info("Telegram image receipt normalized")
        return download_telegram_image(
            file_id,
            os.getenv("TELEGRAM_BOT_TOKEN")
        )

    logger.info("No homework image supplied; running text-only homework workflow")
    return None


def _extract_telegram_file_id(photo):
    if isinstance(photo, list):
        if not photo:
            raise ValueError("Telegram photo list was empty")
        selected = photo[-1]
    else:
        selected = photo

    if isinstance(selected, dict):
        file_id = selected.get("file_id")
    else:
        file_id = selected

    if not file_id:
        raise ValueError("Telegram photo did not include a file_id")
    return file_id

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
