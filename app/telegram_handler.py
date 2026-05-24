from telegram.ext import ApplicationBuilder, MessageHandler, filters


async def handle_text(update, context):
    print(update.message.text)
    await update.message.reply_text("received")


def run_bot(token):
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.run_polling()
