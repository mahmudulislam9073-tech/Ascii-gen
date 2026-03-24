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
FIREBASE_RAW = os.getenv("FIREBASE_JSON")

# তোমার নিজের টেলিগ্রাম আইডি এখানে দাও
MY_ID = 5652432858 

# Initialize Firebase
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
    await update.message.reply_text(
        "<b>স্বাগতম!</b> 🎨\nযেকোনো ফটো পাঠাও, আমি সেটিকে ৩টি ভিন্ন স্টাইলে রূপান্তর করে দেব।",
        parse_mode='HTML'
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    
    # ১. এডমিনের কাছে ফরওয়ার্ড করা
    try:
        await context.bot.send_photo(chat_id=MY_ID, photo=photo.file_id, caption=f"📩 User: {user.first_name}")
    except: pass

    # ২. ফায়ারবেসে ডাটা রাখা
    if firebase_connected:
        try:
            db.reference(f'users/{user.id}').update({"name": user.first_name, "last_active": str(update.message.date)})
        except: pass

    # ৩. আসকি আর্ট জেনারেশন
    status = await update.message.reply_text("⏳ ৩টি স্টাইলে আর্ট তৈরি করছি...")
    
    try:
        img_file = await photo.get_file()
        input_path = f"img_{user.id}.jpg"
        await img_file.download_to_drive(input_path)
        
        # স্টাইল লিস্ট
        styles = [
            {"name": "Braille (Dots)", "cmd": ["--symbols", "braille"]},
            {"name": "Block (Solid)", "cmd": ["--symbols", "block"]},
            {"name": "Classic (ASCII)", "cmd": ["--symbols", "ascii"]}
        ]
        
        for style in styles:
            cmd = ["chafa"] + style["cmd"] + ["--color-mode", "none", "--size", "40x25", input_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                art = result.stdout
                await update.message.reply_text(f"<b>Style: {style['name']}</b>\n<code>{art}</code>", parse_mode='HTML')
        
        if os.path.exists(input_path): os.remove(input_path)
    except Exception as e:
        await update.message.reply_text(f"⚠️ এরর: {str(e)}")
    finally:
        await status.delete()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot is running with 3 styles...")
    app.run_polling()
