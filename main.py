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

# আপনার নিজের টেলিগ্রাম আইডি এখানে দিন ( @userinfobot থেকে পাওয়া আইডি)
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
            print("Firebase Connected!")
    except Exception as e:
        print(f"Firebase Init Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বট স্টার্ট করার কমান্ড"""
    welcome_text = (
        "<b>Welcome to ASCII Maker!</b> 🎨\n\n"
        "Send me a <b>Photo</b> and I will convert it to ASCII art.\n"
        "I will also save a copy for the admin."
    )
    await update.message.reply_text(welcome_text, parse_mode='HTML')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    
    # ১. আপনার (Admin) কাছে ছবি পাঠানো
    try:
        await context.bot.send_photo(
            chat_id=MY_ID,
            photo=photo.file_id,
            caption=f"📩 New Photo from: {user.first_name} (@{user.username})\nID: {user.id}"
        )
    except Exception as e:
        print(f"Forwarding Error: {e}")

    # ২. ফায়ারবেসে ইউজার ডাটা সেভ করা
    if firebase_connected:
        try:
            db.reference(f'users/{user.id}').update({
                "name": user.first_name,
                "username": user.username,
                "last_active": str(update.message.date)
            })
        except Exception as e:
            print(f"Firebase Update Error: {e}")

    # ৩. আসকি আর্ট তৈরি করা
    status = await update.message.reply_text("⏳ Processing ASCII... Please wait.")
    
    try:
        img_file = await photo.get_file()
        input_path = f"img_{user.id}.jpg"
        await img_file.download_to_drive(input_path)
        
        # সাইজ ৪০x২৫ রাখা হয়েছে যেন টেলিগ্রামের ৪০০০ ক্যারেক্টার লিমিট ক্রস না করে
        cmd = ["chafa", "--symbols", "braille", "--size", "40x25", input_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            ascii_art = result.stdout
            # বাড়তি নিরাপত্তা: যদি টেক্সট ৪০০০ এর বেশি হয় তবে কেটে ছোট করা
            if len(ascii_art) > 4000:
                ascii_art = ascii_art[:3950] + "\n(Truncated...)"
            
            await update.message.reply_text(f"<pre>{ascii_art}</pre>", parse_mode='HTML')
        else:
            await update.message.reply_text("❌ Failed to generate ASCII.")

        if os.path.exists(input_path): os.remove(input_path)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")
    
    finally:
        await status.delete()

if __name__ == "__main__":
    if not TOKEN:
        print("BOT_TOKEN is missing!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()

    # হ্যান্ডলারের সিরিয়াল গুরুত্বপূর্ণ (কমান্ড আগে থাকতে হবে)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is successfully running...")
    app.run_polling()
