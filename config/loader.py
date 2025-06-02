# config/loader.py

import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(override=True)

# Instagram
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Email (IMAP) for polling
EMAIL_IMAP_HOST = os.getenv("EMAIL_IMAP_HOST")
EMAIL_ADDRESS   = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")

#Headless mode
HEADLESS = os.getenv("HEADLESS")
# (Any other API keys or custom settings)

