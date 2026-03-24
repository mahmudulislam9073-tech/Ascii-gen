import os
import subprocess
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Retrieve token from GitHub Secrets
TOKEN = os.getenv("BOT_TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("Processing your image into 3 ASCII styles... 🎨")

    try:
        photo_file = await update.message.photo[-1].get_file()
        input_path = "input.jpg"
        await photo_file.download_to_drive(input_path)

        # Style 1: Braille Dots
        cmd1 = ["chafa", "--symbols", "braille", "-c", "none", "--size", "60x40", input_path]
        res1 = subprocess.run(cmd1, capture_output=True, text=True).stdout

        # Style 2: Blocks
        cmd2 = ["chafa", "--symbols", "block", "-c", "none", "--size", "50x30", input_path]
        res2 = subprocess.run(cmd2, capture_output=True, text=True).stdout

        # Style 3: Classic ASCII
        cmd3 = ["chafa", "--symbols", "ascii", "-c", "none", "--size", "50x30", input_path]
        res3 = subprocess.run(cmd3, capture_output=True, text=True).stdout

        # Sending messages using HTML mode
        await update.message.reply_text(f"<b>✨ Style 1: Braille Dots</b>\n<pre>{res1}</pre>", parse_mode='HTML')
        await update.message.reply_text(f"<b>🔳 Style 2: Blocks</b>\n<pre>{res2}</pre>", parse_mode='HTML')
        await update.message.reply_text(f"<b>📜 Style 3: Classic ASCII</b>\n<pre>{res3}</pre>", parse_mode='HTML')

        # Cleanup
        if os.path.exists(input_path): 
            os.remove(input_path)

    except Exception as e:
        await update.message.reply_text(f"Sorry, an error occurred: <code>{e}</code>", parse_mode='HTML')
    
    finally:
        await status_msg.delete()

async def handle_invalid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This will alert the user if they send anything other than a photo
    await update.message.reply_text(
        "⚠️ <b>Invalid Input!</b>\n\nPlease send a <b>Photo</b> to generate ASCII art. Text, stickers, or files are not supported.",
        parse_mode='HTML'
    )

if __name__ == "__main__":
    if not TOKEN:
        print("Error: BOT_TOKEN not found in Secrets!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()

    # Handler for Photos
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Handler for everything else (Text, Stickers, Documents, etc.)
    app.add_handler(MessageHandler(filters.ALL & (~filters.PHOTO), handle_invalid_input))

    print("Bot is running in English with Input Validation...")
    app.run_polling()
