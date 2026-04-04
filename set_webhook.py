"""
Запусти этот скрипт ОДИН РАЗ после деплоя на Vercel
чтобы зарегистрировать webhook в Telegram.

Использование:
  python set_webhook.py
"""

import requests

TELEGRAM_BOT_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
VERCEL_URL = "https://ВАШ_ПРОЕКТ.vercel.app"   # URL твоего деплоя на Vercel
WEBHOOK_SECRET = "mysecret"                      # должен совпадать с WEBHOOK_SECRET в переменных Vercel

webhook_url = f"{VERCEL_URL}/webhook/{WEBHOOK_SECRET}"

response = requests.post(
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
    json={"url": webhook_url, "allowed_updates": ["message", "callback_query"]}
)

print(response.json())
