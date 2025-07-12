from telegram import Update
from telegram.ext import ContextTypes

from db import transaction_handler
from models.notification import get_all_notifications, disable_notification
from utils.scheduler import stop_to_scheduler


@transaction_handler
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    context.bot_data['logger'].info(f'Stop all notifications for chat_id: {chat_id}')
    for ntf in get_all_notifications(context.bot_data['db_session'], chat_id):
        disable_notification(context.bot_data['db_session'], ntf)
        stop_to_scheduler(ntf.id, context.job_queue)

    await update.message.reply_text('Напоминания остановлены.')
