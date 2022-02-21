from telegram import Update
from telegram.ext import CallbackContext


def start_command(update: Update, context: CallbackContext) -> None:
    context.bot.logger.info(f'Start new chat_id {update.message.chat_id}')
    update.message.reply_text('Привет, давай знакомится. Для начала настрой меня /setting.')
