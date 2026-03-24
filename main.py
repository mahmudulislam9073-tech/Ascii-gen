import os
import subprocess
import asyncio
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# গিটহাব সিক্রেটস থেকে টোকেন নেওয়া হবে
TOKEN = os.getenv("BOT_TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("প্রসেসিং হচ্ছে, দয়া করে অপেক্ষা করুন...")

    photo_file = await update.message.photo[-1].get_file()
    input_path = "input.jpg"
    pixel_path = "pixel_art_1k.png"
    await photo_file.download_to_drive(input_path)

    try:
        # ১. ASCII টেক্সট তৈরি (Chafa ব্যবহার করে)
        text_cmd = ["chafa", "--symbols", "braille", "-c", "none", "--color-space", "din99d", input_path]
        text_result = subprocess.run(text_cmd, capture_output=True, text=True)
        
        if text_result.stdout:
            ascii_text = text_result.stdout[:3500] 
            await update.message.reply_text(f"```\n{ascii_text}\n```", parse_mode='MarkdownV2')

        # ২. কালারফুল হাই-রেজ পিক্সেল আর্ট তৈরি (Pillow)
        img = Image.open(input_path)
        original_width, original_height = img.size
        aspect_ratio = original_width / original_height

        pixel_base_width = 100
        pixel_base_height = max(1, int(pixel_base_width / aspect_ratio))
        img_small = img.resize((pixel_base_width, pixel_base_height), resample=Image.BILINEAR)

        # ৩. রেজোলিউশন বড় করা
        target_width = 1024
        target_height = int(target_width / aspect_ratio)
        result_img = img_small.resize((target_width, target_height), resample=Image.NEAREST)
        result_img.save(pixel_path, quality=95)

        # ৪. ছবি পাঠানো
        with open(pixel_path, 'rb') as f:
            await update.message.reply_photo(f, caption="আপনার হাই-রেজ পিক্সেল আর্ট!")

    except Exception as e:
        await update.message.reply_text(f"দুঃখিত, একটি ত্রুটি হয়েছে: {e}")

    finally:
        await status_msg.delete()
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(pixel_path): os.remove(pixel_path)

if __name__ == "__main__":
    if not TOKEN:
        print("Error: BOT_TOKEN not found in Secrets!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("বটটি এখন সচল...")
    app.run_polling()
