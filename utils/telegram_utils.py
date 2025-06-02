# utils/telegram_utils.py

import time
import requests
from config import loader

BOT_TOKEN = loader.TELEGRAM_BOT_TOKEN
CHAT_ID   = loader.TELEGRAM_CHAT_ID
BASE_URL  = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(text: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()

def get_updates(offset: int = None):
    url = f"{BASE_URL}/getUpdates"
    params = {}
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def wait_for_reply(prompt: str, poll_interval: int = 3):
    """
    Send `prompt` to Telegram, then poll getUpdates until user replies text.
    Returns the first non-empty text reply.
    """
    send_message(prompt)
    last_update_id = None

    while True:
        data = get_updates(offset=(last_update_id + 1) if last_update_id else None)
        updates = data.get("result", [])
        for upd in updates:
            last_update_id = upd["update_id"]
            if "message" in upd and str(upd["message"]["chat"]["id"]) == str(CHAT_ID):
                text = upd["message"].get("text", "").strip()
                if text:
                    return text
        time.sleep(poll_interval)
