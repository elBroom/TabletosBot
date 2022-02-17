from telegram import Update
from telegram.ext import CallbackContext

from db import get_notifications, disable_notification
from utils import stop_to_scheduler


def stop_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    for ntf in get_notifications(context.bot_data['db_session'], chat_id):
        disable_notification(context.bot_data['db_session'], ntf)
        stop_to_scheduler(ntf.id, context.job_queue)

    update.message.reply_text('Напоминание остановлены.')