import hashlib
import hmac
import os


def pseudonymous_telegram_user(user_id):
    if user_id is None:
        return "telegram-user"

    salt = os.getenv("USER_ID_SALT")
    if not salt:
        return "telegram-user"

    digest = hmac.new(
        salt.encode("utf-8"),
        str(user_id).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:12]
    return f"telegram-{digest}"


def safe_db_label(path):
    return getattr(path, "name", "homework.db")
