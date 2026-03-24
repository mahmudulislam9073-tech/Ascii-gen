import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your actual token from BotFather
TOKEN = "8632270435:AAFJ0JyyuD7DDmhhNvlBtr7solO0CsmXrIU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a photo and I'll 'Chafafy' it into ASCII art for you.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Download the photo
    photo_file = await update.message.photo[-1].get_file()
    input_path = "input_image.jpg"
    await photo_file.download_to_drive(input_path)

    try:
        # 2. Run Chafa via subprocess
        # --symbols ascii: ensures it works in standard text
        # --size 60x: keeps it narrow enough for mobile screens
        # -c none: removes terminal color codes for clean text
        cmd = ["chafa", "--symbols", "ascii", "-c", "none", "--size", "60x", input_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        ascii_art = result.stdout

        # 3. Wrap in backticks (```) to ensure monospaced formatting on Telegram
        formatted_message = f"```\n{ascii_art}\n```"
        
        await update.message.reply_text(formatted_message, parse_mode="MarkdownV2")

    except Exception as e:
        await update.message.reply_text(f"Error processing image: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Bot is running...")
    app.run_polling()
