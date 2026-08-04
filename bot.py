import asyncio
import os
from flask import Flask
from threading import Thread
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ===== КОНФИГУРАЦИЯ =====
TOKEN = "8946618214:AAFNCum0l_MS0x_w9ZlNYmridM4TYIEuzbs"
ADMIN_CHAT_ID = 8842769815  # число, без кавычек

START_MESSAGE = """
📌 Добро пожаловать!

Доступ в закрытый канал — 1500 ₽.
Нажми «💳 Оплатить», чтобы получить реквизиты.
"""

PAYMENT_MESSAGE = """
💳 Реквизиты для оплаты:

Карта: 5469 1600 1745 0870
Сумма: 1500 ₽

После оплаты нажми «📨 Я оплатил» и отправь скриншот.
"""

CONFIRM_MESSAGE = """
📸 Отправь, пожалуйста, скриншот перевода.
Мы сверим данные и предоставим доступ.
"""

THANK_MESSAGE = """
✅ Спасибо! Твой платёж получен.
Доступ будет предоставлен в течение 5 минут.
"""

# ===== ОБРАБОТЧИКИ БОТА =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(START_MESSAGE, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатить", callback_data="pay")]
    ]))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pay":
        await query.edit_message_text(PAYMENT_MESSAGE, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📨 Я оплатил", callback_data="confirm")]
        ]))
    elif query.data == "confirm":
        await query.edit_message_text(CONFIRM_MESSAGE)
        context.user_data['waiting_for_screenshot'] = True

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_screenshot'):
        await update.message.reply_text("Сначала нажми «📨 Я оплатил».")
        return

    user = update.message.from_user
    user_id = user.id
    user_name = user.full_name
    user_username = user.username or "Нет username"

    admin_message = (
        f"📩 *Новая заявка!*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 {user_name}\n"
        f"🆔 `{user_id}`\n"
        f"💬 @{user_username}\n"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message, parse_mode="Markdown")

    if update.message.photo:
        photo = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo, caption="🧾 Скриншот оплаты")
    else:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text="⚠️ Пользователь не отправил скриншот.")

    await update.message.reply_text(THANK_MESSAGE)
    context.user_data['waiting_for_screenshot'] = False

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    app.run_polling()

# ===== ВЕБ-СЕРВЕР ДЛЯ RENDER =====
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

@flask_app.route('/health')
def health():
    return "OK"

def run_bot():
    main()

# ===== ГЛАВНЫЙ ЗАПУСК =====
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    Thread(target=run_bot).start()
    # Запускаем веб-сервер для Render
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)