import logging

logger = logging.getLogger(__name__)


# def download_telegram_image(file_id: str, bot_token: str):
#     """
#     1. get file path
#     2. download actual image bytes
#     """

#     # Step 1: get file path
#     url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
#     resp = requests.get(url).json()

#     file_path = resp["result"]["file_path"]

#     # Step 2: download image
#     file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"

#     img = requests.get(file_url).content
#     return img


def download_telegram_image(file_id: str, bot_token: str):
    if not bot_token:
        logger.error("Cannot download Telegram image: TELEGRAM_BOT_TOKEN not set")
        raise ValueError("TELEGRAM_BOT_TOKEN not set")

    import requests

    logger.info("Requesting Telegram file metadata", extra={"file_id": file_id})
    url = f"https://api.telegram.org/bot{bot_token}/getFile"
    response = requests.get(url, params={"file_id": file_id}, timeout=30)
    resp = response.json()

    if not resp.get("ok"):
        logger.error("Telegram getFile failed", extra={"file_id": file_id, "status_code": response.status_code})
        raise RuntimeError(f"Telegram API error: {resp}")

    file_path = resp["result"]["file_path"]

    logger.info("Downloading Telegram image bytes", extra={"file_id": file_id, "file_path": file_path})
    file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    file_response = requests.get(file_url, timeout=30)
    file_response.raise_for_status()
    img = file_response.content
    logger.info("Telegram image downloaded", extra={"file_id": file_id, "image_bytes": len(img)})

    return img
