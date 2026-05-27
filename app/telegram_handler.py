import asyncio
import logging
import os

from telegram.ext import ApplicationBuilder, MessageHandler, filters

from app.main import format_reply, run

logger = logging.getLogger(__name__)


def _telegram_event(update):
    message = update.message
    user = message.from_user
    username = user.username or user.full_name or str(user.id)
    photo = []

    if message.photo:
        photo = [{"file_id": item.file_id, "width": item.width, "height": item.height} for item in message.photo]

    event = {
        "user": username,
        "text": message.text or message.caption or "",
    }

    if photo:
        event["photo"] = photo

    return event


async def handle_text(update, context):
    logger.info("Telegram text message received", extra={"chat_id": update.effective_chat.id})
    event = _telegram_event(update)
    result = await asyncio.to_thread(run, event)
    await update.message.reply_text(format_reply(result).get("answer", "received"))


async def handle_photo(update, context):
    logger.info("Telegram image message received", extra={"chat_id": update.effective_chat.id})
    event = _telegram_event(update)
    result = await asyncio.to_thread(run, event)
    reply = format_reply(result).get("answer") or result.get("error") or "Unable to analyze this homework image."
    await update.message.reply_text(reply)


def run_bot(token):
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger.info("Starting Telegram homework helper bot")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.run_polling()
