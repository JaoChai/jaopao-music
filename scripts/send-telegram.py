#!/usr/bin/env python3
"""Send Telegram message via specific bot token — ใช้ร่วมกันทุก agent"""

import json
import sys
import urllib.request

def send(bot_token, chat_id, text):
    """ส่งข้อความผ่าน Telegram Bot API"""
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        if data.get("ok"):
            print(f"[send-telegram] Sent to {chat_id} via bot ...{bot_token[-8:]}")
            return True
        else:
            print(f"[send-telegram] Error: {data}")
            return False
    except Exception as e:
        print(f"[send-telegram] Failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: send-telegram.py <bot_token> <chat_id> <message>")
        sys.exit(1)

    bot_token = sys.argv[1]
    chat_id = sys.argv[2]
    message = " ".join(sys.argv[3:])

    # Also read from stdin if message is "-"
    if message == "-":
        message = sys.stdin.read()

    success = send(bot_token, chat_id, message)
    sys.exit(0 if success else 1)
