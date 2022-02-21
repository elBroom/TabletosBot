import re

from telegram import Update
from telegram.ext import CallbackContext


from db import NoResultFoundErr
from models.notification import Notification, get_notification
from models.history import History, get_history_row


def get_notification_from_query(update: Update, context: CallbackContext) -> Notification:
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    try:
        num = re.match(r"^\w+ (?P<num>\d+)$", query.data).group('num')
        return get_notification(context.bot_data['db_session'], int(num), chat_id)
    except (LookupError, ValueError):
        query.message.reply_text('Не верный формат num')
    except NoResultFoundErr:
        query.message.reply_text('Напоминание не найдено.')


def get_history_from_query(update: Update, context: CallbackContext) -> History:
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    try:
        num = re.match(r"^\w+ (?P<num>\d+)$", query.data).group('num')
        return get_history_row(context.bot_data['db_session'], int(num), chat_id)
    except (LookupError, ValueError):
        query.message.reply_text('Не верный формат num')
    except NoResultFoundErr:
        query.message.reply_text('Запись не найдена.')
