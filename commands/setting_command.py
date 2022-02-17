from telegram import Update
from telegram.ext import CallbackContext


def setting_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Напоминание остановлены.')
