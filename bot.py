import os
import telebot
from flask import Flask
from threading import Thread
from telebot.types import ChatJoinRequest

# ===== КОНФИГУРАЦИЯ =====
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ Нет токена! Добавь TELEGRAM_TOKEN в переменные окружения Render.")

ADMIN_CHAT_ID = 8842769815  # ЗАМЕНИ НА СВОЙ TELEGRAM ID (число)

bot = telebot.TeleBot(TOKEN)

# ===== КЛАВИАТУРЫ =====
def main_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("💳 Оплатить", callback_data="pay"))
    return keyboard

def confirm_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("📨 Я оплатил", callback_data="confirm"))
    return keyboard

# ===== ОБРАБОТЧИКИ БОТА =====

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "📌 Добро пожаловать!\n\nДоступ в приватный канал — 1000 ₽.\nНажми «💳 Оплатить», чтобы получить реквизиты.",
        reply_markup=main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "pay":
        bot.edit_message_text(
            "💳 Реквизиты для оплаты:\n\nКарта: 5379 6530 1364 0105\nСумма: 1000 ₽\n\nПосле оплаты нажми «📨 Я оплатил» и отправь скриншот.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=confirm_keyboard()
        )
        bot.answer_callback_query(call.id)

    elif call.data == "confirm":
        bot.edit_message_text(
            "📸 Отправь, пожалуйста, скриншот перевода.\nМы переповерим все и предоставим доступ.",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_username = message.from_user.username or "Нет username"

    admin_message = (
        f"📩 *Новая заявка!*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 {user_name}\n"
        f"🆔 `{user_id}`\n"
        f"💬 @{user_username}\n"
    )

    bot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode="Markdown")
    bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id, caption="🧾 Скриншот оплаты")

    bot.reply_to(message, "✅ Спасибо! Твой платёж получен.\nДоступ будет предоставлен в течение 5 минут.")

# ===== НОВЫЙ ОБРАБОТЧИК ЗАЯВОК НА ВСТУПЛЕНИЕ =====
@bot.chat_join_request_handler()
def handle_join_request(message: ChatJoinRequest):
    bot.send_message(
        message.from_user.id,
        "👋 Ты оставил заявку в приватный канал.\n\n"
        "💰 Доступ стоит 1000 ₽.\n"
        "Для оплаты нажми /start в этом боте.\n\n"
        "После оплаты я добавлю тебя в канал."
    )

# ===== ЗАПУСК БОТА =====
def run_bot():
    print("🤖 Удаляю старый вебхук...")
    bot.remove_webhook()
    print("🤖 Бот запущен!")
    bot.infinity_polling()

# ===== ВЕБ-СЕРВЕР ДЛЯ RENDER =====
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

@flask_app.route('/health')
def health():
    return "OK"

# ===== ГЛАВНЫЙ ЗАПУСК =====
if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
