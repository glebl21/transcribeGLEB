import hashlib
import logging
import os
import tempfile
from collections import defaultdict

import requests
import telebot
from flask import Flask, request, abort
from groq import Groq
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "mysecret")

MAX_TELEGRAM_MESSAGE_LENGTH = 4096

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is required")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

transcription_store = {}
stats = defaultdict(lambda: {"count": 0, "summaries": 0})


# ─────────────────────────────────────────────
# Утилиты
# ─────────────────────────────────────────────

def store_text(text):
    key = hashlib.md5(text.encode()).hexdigest()[:16]
    transcription_store[key] = text
    return key


def get_text(key):
    return transcription_store.get(key)


def split_for_telegram(text, max_len=MAX_TELEGRAM_MESSAGE_LENGTH):
    chunks = []
    remaining = text.strip()
    while len(remaining) > max_len:
        split_at = remaining.rfind("\n", 0, max_len)
        if split_at <= 0:
            split_at = max_len
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


def download_telegram_file(file_path):
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    for attempt in range(3):
        try:
            response = requests.get(file_url, timeout=60)
            response.raise_for_status()
            return response.content
        except Exception as e:
            if attempt == 2:
                raise
            import time
            time.sleep(2)


def transcribe_audio(audio_bytes, filename="audio.ogg"):
    ext = os.path.splitext(filename)[1] or ".ogg"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=(filename, audio_file.read()),
                model="whisper-large-v3",
                language=None,
                response_format="text",
            )
        return transcription.strip()
    finally:
        os.unlink(tmp_path)


def summarize_text(text):
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": (
                "Сделай краткое саммари этого текста. "
                "Выдели ключевые мысли и выводы. "
                "Отвечай на том же языке что и текст. "
                "Используй маркированный список (•).\n\n" + text
            )}]}]}
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                return {"text": result, "model": "Gemini 2.0 Flash ✨"}
        except Exception:
            logger.exception("Gemini failed, fallback to Groq")

    result = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": (
                "Сделай краткое саммари текста. "
                "Выдели ключевые мысли и выводы. "
                "Отвечай на том же языке что и текст. "
                "Используй маркированный список (•)."
            )},
            {"role": "user", "content": text},
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        temperature=0.4,
    )
    return {"text": result.choices[0].message.content.strip(), "model": "Groq LLaMA 3.3 70B ⚡"}


def make_keyboard(text_key):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📝 Краткое изложение", callback_data=f"sum:{text_key}"))
    return keyboard


# ─────────────────────────────────────────────
# Обработка аудио
# ─────────────────────────────────────────────

def process_audio(message, file_id, filename="audio.ogg"):
    chat_id = message.chat.id
    user_id = message.from_user.id
    status_msg = bot.reply_to(message, "⏳ Транскрибирую...")
    try:
        file_info = bot.get_file(file_id)
        if file_info.file_size and file_info.file_size > 19 * 1024 * 1024:
            bot.edit_message_text(
                "❌ Файл слишком большой. Максимум 20 МБ.",
                chat_id=chat_id, message_id=status_msg.message_id,
            )
            return

        audio_bytes = download_telegram_file(file_info.file_path)
        text = transcribe_audio(audio_bytes, filename)
        if not text:
            bot.edit_message_text("❌ Не удалось распознать речь.", chat_id=chat_id, message_id=status_msg.message_id)
            return

        stats[user_id]["count"] += 1
        text_key = store_text(text)
        parts = split_for_telegram(f"📄 Транскрипция:\n\n{text}")

        bot.edit_message_text(
            parts[0], chat_id=chat_id, message_id=status_msg.message_id,
            reply_markup=make_keyboard(text_key),
        )
        for part in parts[1:]:
            bot.send_message(chat_id=chat_id, text=part)

    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {str(e)}", chat_id=chat_id, message_id=status_msg.message_id)
        logger.exception("Failed to process audio")


# ─────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────

@bot.message_handler(commands=["start", "help"])
def handle_start(message):
    bot.reply_to(
        message,
        "🎙️ *Бот-транскрибатор голосовых сообщений*\n\n"
        "Отправь голосовое, кружок или аудиофайл — переведу в текст!\n\n"
        "🔧 *Что умею:*\n"
        "• Транскрибация голосовых и кружков\n"
        "• Аудиофайлы MP3, OGG, WAV, M4A, FLAC\n"
        "• Кнопка 📝 Краткое изложение после транскрибации\n"
        "• /stats — твоя статистика\n\n"
        "Просто отправь голосовое! 🎤",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["stats"])
def handle_stats(message):
    user_id = message.from_user.id
    count = stats[user_id]["count"]
    summaries = stats[user_id]["summaries"]
    bot.reply_to(
        message,
        f"📊 *Твоя статистика:*\n\n"
        f"• Транскрибировано: *{count}* сообщений\n"
        f"• Саммари сделано: *{summaries}*",
        parse_mode="Markdown",
    )


@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    process_audio(message, message.voice.file_id, "voice.ogg")


@bot.message_handler(content_types=["video_note"])
def handle_video_note(message):
    process_audio(message, message.video_note.file_id, "video_note.mp4")


@bot.message_handler(content_types=["audio"])
def handle_audio(message):
    filename = message.audio.file_name or "audio.mp3"
    process_audio(message, message.audio.file_id, filename)


@bot.message_handler(content_types=["document"])
def handle_document(message):
    mime = message.document.mime_type or ""
    filename = (message.document.file_name or "").lower()
    allowed = ["audio/mpeg","audio/ogg","audio/wav","audio/x-wav","audio/mp4",
               "audio/m4a","audio/x-m4a","audio/flac","audio/webm","video/mp4","video/webm"]
    supported_ext = (".mp3",".ogg",".wav",".m4a",".flac",".webm",".mp4")
    if mime in allowed or mime.startswith("audio/") or filename.endswith(supported_ext):
        process_audio(message, message.document.file_id, message.document.file_name or "audio.ogg")


@bot.callback_query_handler(func=lambda call: call.data.startswith("sum:"))
def handle_summary(call):
    try:
        text_key = call.data.split(":", 1)[1]
        text = get_text(text_key)
        if not text:
            bot.answer_callback_query(call.id, "❌ Отправь голосовое заново.", show_alert=True)
            return
        bot.answer_callback_query(call.id, "⏳ Генерирую саммари...")
        summary = summarize_text(text)
        stats[call.from_user.id]["summaries"] += 1
        summary_text = f"📝 Краткое изложение (от {summary['model']}):\n\n{summary['text']}"
        for chunk in split_for_telegram(summary_text):
            bot.send_message(chat_id=call.message.chat.id, text=chunk,
                             reply_to_message_id=call.message.message_id)
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка: {str(e)}", show_alert=True)
        logger.exception("Failed to generate summary")


# ─────────────────────────────────────────────
# Flask webhook endpoint
# ─────────────────────────────────────────────

@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") != "application/json":
        abort(403)
    update = telebot.types.Update.de_json(request.get_data(as_text=True))
    bot.process_new_updates([update])
    return "ok", 200


@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot is running!", 200


if __name__ == "__main__":
    # Локальный запуск через polling
    logger.info("🤖 Бот запущен локально (polling)!")
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=60,
                         allowed_updates=["message", "callback_query"])
