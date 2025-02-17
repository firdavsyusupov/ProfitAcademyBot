import logging
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler, filters
)
from bot.models import User

TOKEN = '7755272758:AAFSgW-B31J9jn6TZduMkif6OKM9M-q7qQg'
logger = logging.getLogger(__name__)

NAME, CITY, PHONE = range(3)

async def start(update: Update, context) -> int:
    await update.message.reply_text("Assalomu alaykum! Ro'yxatdan o'tish uchun ismingizni kiriting.")
    return NAME

async def get_name(update: Update, context) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Shahringiz yoki viloyatingizni kiriting:")
    return CITY

async def get_city(update: Update, context) -> int:
    context.user_data['city'] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting:")
    return PHONE

async def get_phone(update: Update, context) -> int:
    context.user_data['phone'] = update.message.text
    user = User.objects.create(
        telegram_id=update.message.from_user.id,
        name=context.user_data['name'],
        city=context.user_data['city'],
        phone=context.user_data['phone']
    )
    await update.message.reply_text(f"Tabriklaymiz, {user.name}! Siz ro'yxatdan o'tdingiz.")
    return ConversationHandler.END

async def cancel(update: Update, context) -> int:
    await update.message.reply_text("Ro'yxatdan o'tish bekor qilindi.")
    return ConversationHandler.END

class Command(BaseCommand):
    help = 'Запуск Телеграм-бота'

    def handle(self, *args, **options):
        app = Application.builder().token(TOKEN).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
                PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        app.add_handler(conv_handler)
        app.run_polling()
