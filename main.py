import os
import subprocess
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# Retrieve token from GitHub Secrets
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the command /start or /help is issued."""
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
    """Processes the photo and sends 3 different ASCII styles."""
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

        # Sending results via HTML
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
    """Alerts the user if they send anything other than a photo or command."""
    await update.message.reply_text(
        "⚠️ <b>Invalid Input!</b>\n\nPlease send a <b>Photo</b> to generate ASCII art. Text, stickers, or files are not supported.",
        parse_mode='HTML'
    )

if __name__ == "__main__":
    if not TOKEN:
        print("Error: BOT_TOKEN not found in Secrets!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))

    # Photo Handler
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Invalid Input Handler (Everything except photos and commands)
    app.add_handler(MessageHandler(filters.ALL & (~filters.PHOTO) & (~filters.COMMAND), handle_invalid_input))

    print("Bot is fully updated and running...")
    app.run_polling()
