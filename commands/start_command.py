from telegram import Update
from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.bot_data['logger'].warn(f'Start new chat_id {update.message.chat_id} ({update.message.chat.username})')
    await update.message.reply_text('Привет, давай знакомится. Для начала настрой меня /setting.')
