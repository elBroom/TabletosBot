from telegram import Update
from telegram.ext import ContextTypes

from db import transaction_handler
from models.notification import del_notifications, get_all_notifications
from utils.scheduler import stop_to_scheduler


@transaction_handler
async def clean_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    context.bot_data['logger'].info(f'Clean all notification for chat_id: {chat_id}')
    for ntf in get_all_notifications(context.bot_data['db_session'], chat_id):
        stop_to_scheduler(ntf.id, context.job_queue)
        del_notifications(context.bot_data['db_session'], ntf)

    await update.message.reply_text('Добавь новое напоминание /new.')
