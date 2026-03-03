import logging
import asyncio
import os
from telegram import Update
from telegram.ext import (Application, CommandHandler, MessageHandler, ContextTypes, filters)

TOKEN = "8560365838:AAGfUiHeSw0_uMaaV5gZ5-n2n4zs7-RdXfg"
DB_FILE = "gallery.txt" # Файл для хранения данных

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Функция загрузки данных из файла
def load_gallery():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return [line.strip() for line in f.readlines()]
    return []

# Функция сохранения данных в файл
def save_to_gallery(item):
    with open(DB_FILE, "a") as f:
        f.write(item + "\n")

gallery = load_gallery()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот-галерея. Отправляй мне фото или ссылки.\n\n"
        "Проверь мой функционал: /help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 **Список доступных команд:**\n\n"
        "/start - Запустить бота\n"
        "/help - Показать это меню\n"
        "/last - Показать последнее сохраненное фото\n"
        "/all - Показать всю коллекцию по очереди\n\n"
        "📸 **Как сохранять:**\n"
        "Просто пришли мне фото как файл или прямую ссылку на картинку (http...)."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id
    gallery.append(photo_id)
    save_to_gallery(photo_id) # Сохраняем в файл
    await update.message.reply_text(f"Фото сохранено! Всего в базе: {len(gallery)}")

async def echo_or_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("http"):
        try:
            await update.message.reply_photo(photo=text, caption="Сохранил ссылку!")
            gallery.append(text)
            save_to_gallery(text) # Сохраняем ссылку в файл
        except Exception:
            await update.message.reply_text("Не удалось загрузить фото по ссылке.")
    else:
        await update.message.reply_text(f"Ты написал: {text}\nЧтобы узнать, что я умею, введи /help")

async def show_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not gallery:
        return await update.message.reply_text("Галерея пока пуста.")
    await update.message.reply_photo(photo=gallery[-1], caption="Последний добавленный объект")

async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not gallery:
        return await update.message.reply_text("Пока нечего показывать.")
    
    await update.message.reply_text(f"Вывожу всю коллекцию ({len(gallery)} шт.):")
    for item in gallery:
        try:
            await update.message.reply_photo(photo=item)
            await asyncio.sleep(0.5)
        except Exception:
            continue

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("last", show_last))
    app.add_handler(CommandHandler("all", show_all))

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_or_link))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()