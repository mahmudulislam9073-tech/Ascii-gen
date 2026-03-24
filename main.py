import os
import subprocess
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# গিটহাব সিক্রেটস থেকে টোকেন নেওয়া হবে
TOKEN = os.getenv("BOT_TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("আপনার জন্য ৩ ধরনের আসকি আর্ট তৈরি করছি... 🎨")

    photo_file = await update.message.photo[-1].get_file()
    input_path = "input.jpg"
    await photo_file.download_to_drive(input_path)

    try:
        # ১. স্টাইল: Braille (ব্রেইল ডট দিয়ে তৈরি - ডিটেইল বেশি থাকে)
        cmd1 = ["chafa", "--symbols", "braille", "-c", "none", "--size", "60x40", input_path]
        res1 = subprocess.run(cmd1, capture_output=True, text=True).stdout[:3800]

        # ২. স্টাইল: Block (বক্স এবং ব্লক দিয়ে তৈরি - বোল্ড লুক)
        cmd2 = ["chafa", "--symbols", "block", "-c", "none", "--size", "50x30", input_path]
        res2 = subprocess.run(cmd2, capture_output=True, text=True).stdout[:3800]

        # ৩. স্টাইল: Classic ASCII (লেটার এবং সিম্বল দিয়ে তৈরি - ওল্ড স্কুল লুক)
        cmd3 = ["chafa", "--symbols", "ascii", "-c", "none", "--size", "50x30", input_path]
        res3 = subprocess.run(cmd3, capture_output=True, text=True).stdout[:3800]

        # মেসেজগুলো পাঠানো হচ্ছে
        await update.message.reply_text(f"✨ **Style 1: Braille Dots**\n```\n{res1}\n```", parse_mode='MarkdownV2')
        await update.message.reply_text(f"🔳 **Style 2: Blocks**\n```\n{res2}\n```", parse_mode='MarkdownV2')
        await update.message.reply_text(f"📜 **Style 3: Classic ASCII**\n```\n{res3}\n```", parse_mode='MarkdownV2')

    except Exception as e:
        await update.message.reply_text(f"দুঃখিত, সমস্যা হয়েছে: {e}")

    finally:
        await status_msg.delete()
        if os.path.exists(input_path): os.remove(input_path)

if __name__ == "__main__":
    if not TOKEN:
        print("Error: BOT_TOKEN not found!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("বটটি ৩টি মোডে কাজ করার জন্য প্রস্তুত!")
    app.run_polling()
