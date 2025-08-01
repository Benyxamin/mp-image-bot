import os
import uuid
import asyncio
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TOKEN_FILE = "tokens.json"
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        token_db = json.load(f)
else:
    token_db = {}

ADMIN_ID = 8306376632


def save_token_db():
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_db, f)


async def upload_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ فقط ادمین می‌تونه فایل آپلود کنه.")
        return

    photo = update.message.photo[-1]
    tg_file = await photo.get_file()
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.jpg")
    await tg_file.download_to_drive(file_path)

    token_db[unique_id] = file_path
    save_token_db()

    await update.message.reply_text(f"✅ آپلود شد!\nلینک: `/get {unique_id}`", parse_mode="Markdown")


async def handle_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        token = context.args[0]
    except IndexError:
        await update.message.reply_text("❗فرمت درست:\n/get <توکن>")
        return

    if token not in token_db:
        await update.message.reply_text("❌ لینک نامعتبر است یا منقضی شده.")
        return

    file_path = token_db[token]
    sent = await update.message.reply_photo(photo=open(file_path, "rb"))

    await asyncio.sleep(30)
    await sent.delete()
    await update.message.delete()


if __name__ == "__main__":
    import os
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if not BOT_TOKEN:
        print("خطا: توکن ربات تعریف نشده در متغیر محیطی BOT_TOKEN")
        exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.PHOTO, upload_image))
    app.add_handler(CommandHandler("get", handle_get))

    print("🤖 ربات در حال اجراست...")
    app.run_polling()
