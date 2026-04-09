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

---

## 🚀 Деплой на Render.com

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
- **Start Command**: `gunicorn bot:app --bind 0.0.0.0:$PORT --timeout 120`
- **Instance Type**: `Free`

### Шаг 3: Добавь переменные окружения
В разделе **Environment Variables** добавь:
- `TELEGRAM_BOT_TOKEN` = твой токен от BotFather
- `GROQ_API_KEY` = твой Groq API ключ
- `OPENAI_API_KEY` = твой OpenAI API ключ
- `WEBHOOK_SECRET` = любой секретный ключ (например `mysecret123`)

> Render автоматически задаёт `RENDER_EXTERNAL_URL` — бот сам настроит вебхук.

### Шаг 4: Деплой
Нажми **Create Web Service** — бот автоматически задеплоится и настроит вебхук!

---

## 🚂 Деплой на Railway

### Шаг 1: Создай проект
1. Зайди на **https://railway.com** и зарегистрируйся
2. Нажми **New Project** → **Deploy from GitHub repo**
3. Подключи репозиторий: `https://github.com/glebl21/transcribeGLEB.git`

### Шаг 2: Добавь переменные окружения
В настройках сервиса (Variables) добавь:
- `TELEGRAM_BOT_TOKEN` = твой токен от BotFather
- `GROQ_API_KEY` = твой Groq API ключ
- `OPENAI_API_KEY` = твой OpenAI API ключ
- `WEBHOOK_SECRET` = любой секретный ключ

### Шаг 3: Настрой домен
1. Перейди в **Settings → Networking → Public Networking**
2. Нажми **Generate Domain** (получишь `*.up.railway.app`)

> Railway автоматически задаёт `RAILWAY_PUBLIC_DOMAIN` — бот сам настроит вебхук.

### Шаг 4: Деплой
Railway автоматически задеплоит бот после коммита в main!

---

## ✨ Возможности бота

| Функция | Описание |
|---|---|
| 🎤 Голосовые сообщения | Транскрибирует ГС из Telegram |
| 🔵 Кружки (видеосообщения) | Транскрибирует видеокружки |
| 🎵 Аудио файлы | MP3, OGG, WAV, M4A, FLAC и другие форматы |
| 🌍 Автоопределение языка | Русский, английский и 50+ языков |
| 📝 Краткое изложение | Саммари через GPT-5.4 одной кнопкой |
| 📊 Статистика | Команда /stats показывает использование |

---

## 🤖 Как пользоваться

1. Запусти бота командой `/start`
2. Отправь **голосовое сообщение**, **кружок** или **аудиофайл**
3. Получи **транскрипцию текста**
4. Нажми кнопку **📝 Краткое изложение** для саммари

---

## 🛠️ Используемые технологии

- **Groq Whisper Large V3 Turbo** — быстрая и точная модель для транскрибации (бесплатно)
- **OpenAI GPT-5.4** — frontier модель для саммари
- **pyTelegramBotAPI** — работа с Telegram API
- **Flask + Gunicorn** — webhook-сервер для продакшена

---

## 💻 Локальный запуск

```bash
pip install -r requirements.txt

export TELEGRAM_BOT_TOKEN="твой_токен"
export GROQ_API_KEY="твой_groq_ключ"
export OPENAI_API_KEY="твой_openai_ключ"

python bot.py
```

При локальном запуске бот работает в режиме polling (без вебхука).
