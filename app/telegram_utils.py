import logging

logger = logging.getLogger(__name__)


def download_telegram_image(file_id: str, bot_token: str):
    if not bot_token:
        logger.error("Cannot download Telegram image: TELEGRAM_BOT_TOKEN not set")
        raise ValueError("TELEGRAM_BOT_TOKEN not set")

    import requests

    logger.info("Requesting Telegram file metadata")
    url = f"https://api.telegram.org/bot{bot_token}/getFile"
    try:
        response = requests.get(url, params={"file_id": file_id}, timeout=30)
    except requests.RequestException:
        raise RuntimeError("Telegram API request failed while fetching file metadata") from None
    resp = response.json()

    if not resp.get("ok"):
        logger.error("Telegram getFile failed", extra={"status_code": response.status_code})
        raise RuntimeError("Telegram API error while fetching file metadata")

    file_path = resp["result"]["file_path"]

    logger.info("Downloading Telegram image bytes")
    file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    try:
        file_response = requests.get(file_url, timeout=30)
        if not file_response.ok:
            raise RuntimeError("Telegram API error while downloading image")
    except requests.RequestException:
        raise RuntimeError("Telegram API request failed while downloading image") from None
    img = file_response.content
    logger.info("Telegram image downloaded", extra={"image_bytes": len(img)})

    return img
