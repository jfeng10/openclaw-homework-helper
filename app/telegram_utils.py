import requests
import os


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
        raise ValueError("TELEGRAM_BOT_TOKEN not set")

    url = f"https://api.telegram.org/bot{bot_token}/getFile"
    resp = requests.get(url, params={"file_id": file_id}).json()

    # ✅ SAFETY CHECK 1
    if not resp.get("ok"):
        raise RuntimeError(f"Telegram API error: {resp}")

    file_path = resp["result"]["file_path"]

    file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    img = requests.get(file_url).content

    return img