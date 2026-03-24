import os
import subprocess
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# গিটহাব সেটিংস থেকে টোকেনটি পড়বে
TOKEN = os.getenv("BOT_TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("প্রসেসিং হচ্ছে... একটু অপেক্ষা করুন।")

    photo_file = await update.message.photo[-1].get_file()
    input_path = "input.jpg"
    pixel_path = "pixel_art_1k.png"
    await photo_file.download_to_drive(input_path)

    try:
        # ১. ASCII টেক্সট তৈরি (Chafa ব্যবহার করে)
        # এখানে --symbols braille ব্যবহার করা হয়েছে
        text_cmd = ["chafa", "--symbols", "braille", "-c", "none", "--color-space", "rgb", input_path]
        text_result = subprocess.run(text_cmd, capture_output=True, text=True)
        
        # টেক্সট খুব বড় হলে টেলিগ্রাম পাঠাতে পারে না, তাই লিমিট করা ভালো
        await update.message.reply_text(f"
http://googleusercontent.com/immersive_entry_chip/0

---

### ধাপ ৩: গিটহাবে টোকেন সেট করা
১. আপনার গিটহাব রিপোজিটরির **Settings**-এ যান।
২. বাম পাশের মেনু থেকে **Secrets and variables > Actions**-এ ক্লিক করুন।
৩. **New repository secret** বাটনে ক্লিক করুন।
৪. **Name** বক্সে লিখুন: `BOT_TOKEN`
৫. **Secret** বক্সে আপনার টেলিগ্রাম বট টোকেনটি পেস্ট করুন।
৬. **Add secret** ক্লিক করুন।

---

### ধাপ ৪: বটটি চালু করা
১. আপনার রিপোজিটরির **Actions** ট্যাবে ক্লিক করুন।
২. বাম পাশে **Run Telegram Bot** লেখাটিতে ক্লিক করুন।
৩. ডান পাশে **Run workflow** বাটনে ক্লিক করে কাজ শুরু করে দিন।

---

### কিছু জরুরি টিপস:
* **বট অফ হয়ে গেলে:** গিটহাব অ্যাকশন একটানা সর্বোচ্চ ৬ ঘণ্টা চলে। আমি উপরে একটি `cron` জব দিয়েছি যা প্রতি ৬ ঘণ্টা পর পর এটি নিজে থেকেই আবার চালু করবে। এতে আপনি মোটামুটি সব সময় বটটি অনলাইনে পাবেন।
* **ফ্রি লিমিট:** গিটহাবের ফ্রি অ্যাকাউন্টে মাসে ২০০০ মিনিট অ্যাকশন চালানোর সুযোগ থাকে। ২৪ ঘণ্টা চালালে এই লিমিট দ্রুত শেষ হতে পারে। তাই যদি দেখেন লিমিট শেষ, তবে **Koyeb** বা **Render** এর মতো সার্ভিস ব্যবহার করা বুদ্ধিমানের কাজ হবে।

আপনি কি চান আমি আপনাকে **Koyeb**-এ হোস্ট করার সিস্টেমটাও বলে দিই? ওটা একবার সেট করলে আর কখনোই অফ হবে না।
