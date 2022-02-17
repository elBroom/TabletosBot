import re

from telegram import Update
from telegram.ext import CallbackContext


from db import NoResultFound
from models.notification import Notification, get_notification


def get_notification_from_query(update: Update, context: CallbackContext) -> Notification:
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    try:
        nid = re.match(r"^\w+ (?P<nid>\d+)$", query.data).group('nid')
        return get_notification(context.bot_data['db_session'], int(nid), chat_id)
    except (LookupError, ValueError):
        query.message.reply_text('Не верный формат num')
    except NoResultFound:
        query.message.reply_text('Напоминание не найдено.')
