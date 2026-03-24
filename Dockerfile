# পাইথন ইমেজ ব্যবহার করছি
FROM python:3.10-slim

# Chafa এবং প্রয়োজনীয় টুলস ইন্সটল করা
RUN apt-get update && apt-get install -y chafa && rm -rf /var/lib/apt/lists/*

# কাজের ডিরেক্টরি সেট করা
WORKDIR /app

# ফাইলগুলো কপি করা
COPY . .

# লাইব্রেরি ইন্সটল করা
RUN pip install --no-cache-dir -r requirements.txt

# বট রান করা
CMD ["python", "chafa_bot.py"]
