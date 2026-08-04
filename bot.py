import os
import telebot
from flask import Flask
from threading import Thread

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ Нет токена! Добавь TELEGRAM_TOKEN в переменные окружения Render.")

ADMIN_CHAT_ID = 8842769815  # ЗАМЕНИ НА СВОЙ TELEGRAM ID (число)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "✅ Бот работает!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Получил твоё сообщение!")

def run_bot():
    print("🤖 Удаляю старый вебхук...")
    bot.remove_webhook()
    print("🤖 Бот запущен!")
    bot.infinity_polling()

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

@flask_app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
