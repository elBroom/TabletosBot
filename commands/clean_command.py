from telegram import Update
from telegram.ext import CallbackContext

from db import del_notifications, get_notifications
from utils import stop_to_scheduler


def clean_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    for ntf in get_notifications(context.bot_data['db_session'], chat_id):
        stop_to_scheduler(ntf.id, context.job_queue)
        del_notifications(context.bot_data['db_session'], ntf)

    update.message.reply_text('Добавь новое напоминание /new.')
