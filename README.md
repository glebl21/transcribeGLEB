# 🎙️ Telegram Voice Transcriber Bot

Бот транскрибирует голосовые сообщения в текст и умеет делать краткое саммари.  
Использует **Groq Whisper Large V3 Turbo** для транскрибации и **GPT-5.4** для саммари.

---

## 🔑 Получение API ключей

### 1. Telegram Bot Token (бесплатно)
1. Открой Telegram и найди **@BotFather**
2. Напиши `/newbot`
3. Придумай имя и username для бота
4. Скопируй полученный **токен**

### 2. Groq API Key (бесплатно)
1. Перейди на **https://console.groq.com**
2. Зарегистрируйся (через Google или email)
3. Перейди в раздел **API Keys → Create API Key**
4. Скопируй ключ

**Groq бесплатные лимиты:**
- Whisper Large V3 Turbo: 7 200 секунд аудио / час

### 3. OpenAI API Key
1. Перейди на **https://platform.openai.com/api-keys**
2. Зарегистрируйся или войди в аккаунт
3. Нажми **Create new secret key**
4. Скопируй ключ

**GPT-5.4 цены:**
- Input: $2.50 за 1M токенов
- Output: $15 за 1M токенов

---

## 🚀 Деплой на Render.com (бесплатно)

### Шаг 1: Создай Web Service
1. Зайди на **https://render.com** и зарегистрируйся
2. Нажми **New +** → **Web Service**
3. Подключи GitHub репозиторий: `https://github.com/glebl21/transcribeGLEB.git`

### Шаг 2: Настрой сервис
- **Name**: `transcribe-bot` (любое имя)
- **Region**: выбери ближайший регион
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python voice_transcriber_bot.py`
- **Instance Type**: `Free`

### Шаг 3: Добавь переменные окружения
В разделе **Environment Variables** добавь:
- `TELEGRAM_BOT_TOKEN` = твой токен от BotFather
- `GROQ_API_KEY` = твой Groq API ключ
- `OPENAI_API_KEY` = твой OpenAI API ключ

### Шаг 4: Деплой
Нажми **Create Web Service** - бот автоматически задеплоится и запустится!

---

## ✨ Возможности бота

| Функция | Описание |
|---|---|
| 🎤 Голосовые сообщения | Транскрибирует ГС из Telegram |
| 🎵 Аудио файлы | MP3, OGG, WAV, M4A, FLAC и другие форматы |
| 🌍 Автоопределение языка | Русский, английский и 50+ языков |
| 📝 Краткое изложение | Саммари через GPT-5.4 одной кнопкой |
| 📊 Статистика | Команда /stats показывает использование |

---

## 🤖 Как пользоваться

1. Запусти бота командой `/start`
2. Отправь **голосовое сообщение**
3. Получи **транскрипцию текста**
4. Нажми кнопку **📝 Краткое изложение** для саммари

---

## 🛠️ Используемые технологии

- **Groq Whisper Large V3 Turbo** — самая точная и быстрая модель для транскрибации (бесплатно)
- **OpenAI GPT-5.4** — frontier модель для профессиональных задач и саммари
- **pyTelegramBotAPI** — работа с Telegram API

---

## 💻 Локальный запуск

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка переменных окружения
```bash
export TELEGRAM_BOT_TOKEN="твой_токен"
export GROQ_API_KEY="твой_groq_ключ"
export OPENAI_API_KEY="твой_openai_ключ"
```

### Запуск
```bash
python voice_transcriber_bot.py
```
