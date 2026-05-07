"""Optional Telegram notifications for pipeline failures."""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request

from src.config import get_settings


def send_telegram(text: str) -> bool:
    s = get_settings()
    token, chat = s["telegram_bot_token"], s["telegram_chat_id"]
    if not token or not chat:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except urllib.error.URLError:
        return False
