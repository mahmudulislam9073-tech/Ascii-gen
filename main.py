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

# তোমার নিজের টেলিগ্রাম আইডি এখানে দাও
MY_ID = 5652432858 

# ফায়ারবেস সেটআপ
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
    welcome_text = (
        "<b>Welcome to ASCII Maker!</b> 🎨\n\n"
        "Send me a <b>Photo</b> to get 3 unique ASCII styles.\n"
        "<i>Click on the art to copy it!</i>"
    )
    await update.message.reply_text(welcome_text, parse_mode='HTML')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    status_msg = await update.message.reply_text("Processing your image... 🎨")

    try:
        # ১. এডমিন লগ (Saved Messages)
        try:
            await context.bot.send_photo(chat_id=MY_ID, photo=photo.file_id, caption=f"📩 User: {user.first_name}")
        except: pass

        # ২. ফায়ারবেস লগ
        if firebase_connected:
            try:
                db.reference(f'users/{user.id}').update({"name": user.first_name, "last_active": str(update.message.date)})
            except: pass

        # ৩. আসকি আর্ট জেনারেশন
        photo_file = await photo.get_file()
        input_path = f"img_{user.id}.jpg"
        await photo_file.download_to_drive(input_path)

        # ৩টি ভিন্ন স্টাইল (Size optimized for Telegram)
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
                
                # এখানে <code> ট্যাগ ব্যবহার করা হয়েছে যেন ক্লিক করলে কপি হয়
                await update.message.reply_text(
                    f"<b>{style['label']}</b>\n<code>{res}</code>", 
                    parse_mode='HTML'
                )

        if os.path.exists(input_path): os.remove(input_path)

    except Exception as e:
        await update.message.reply_text(f"Error: <code>{e}</code>", parse_mode='HTML')
    finally:
        await status_msg.delete()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot is running...")
    app.run_polling()
