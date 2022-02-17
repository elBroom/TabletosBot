from telegram import Update
from telegram.ext import CallbackContext


def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет, давай знакомится. Для начала настрой меня /setting.')
