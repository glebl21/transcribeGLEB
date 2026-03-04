import os
import hashlib
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import tempfile
from groq import Groq

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

transcription_store = {}


def store_text(text):
    key = hashlib.md5(text.encode()).hexdigest()[:16]
    transcription_store[key] = text
    return key


def get_text(key):
    return transcription_store.get(key)


def download_telegram_file(file_id):
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
    response = requests.get(file_url, timeout=60)
    response.raise_for_status()
    return response.content


def transcribe_audio(audio_bytes, filename="audio.ogg"):
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
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
    result = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты помощник, который делает краткое резюме голосовых сообщений. "
                    "Выдели ключевые мысли и выводы. "
                    "Отвечай на том же языке, что и текст. "
                    "Используй маркированный список (•)."
                ),
            },
            {"role": "user", "content": f"Сделай краткое саммари:\n\n{text}"},
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        temperature=0.4,
    )
    return result.choices[0].message.content.strip()


def make_keyboard(text_key):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📝 Краткое изложение", callback_data=f"sum:{text_key}"))
    return keyboard


def process_audio(message, file_id, filename="audio.ogg"):
    chat_id = message.chat.id
    status_msg = bot.reply_to(message, "⏳ Транскрибирую...")
    try:
        audio_bytes = download_telegram_file(file_id)
        text = transcribe_audio(audio_bytes, filename)
        if not text:
            bot.edit_message_text("❌ Не удалось распознать речь.", chat_id=chat_id, message_id=status_msg.message_id)
            return
        text_key = store_text(text)
        bot.edit_message_text(
            f"📄 *Транскрипция:*\n\n{text}",
            chat_id=chat_id,
            message_id=status_msg.message_id,
            parse_mode="Markdown",
            reply_markup=make_keyboard(text_key)
        )
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {str(e)}", chat_id=chat_id, message_id=status_msg.message_id)
        print(f"[ERROR] {e}")


@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    process_audio(message, message.voice.file_id, "voice.ogg")


@bot.message_handler(content_types=["video_note"])
def handle_video_note(message):
    process_audio(message, message.video_note.file_id, "video_note.mp4")


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
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"📝 *Краткое изложение:*\n\n{summary}",
            parse_mode="Markdown",
            reply_to_message_id=call.message.message_id
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка: {str(e)}", show_alert=True)
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    print("🤖 Бот запущен!")
    bot.infinity_polling(timeout=60, long_polling_timeout=60, allowed_updates=["message", "callback_query"])
