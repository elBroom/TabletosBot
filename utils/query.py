import re

from telegram import Update
from telegram.ext import ContextTypes


from db import NoResultFound
from models.notification import Notification, get_notification
from models.history import History, get_history_row


async def get_notification_from_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Notification:
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    try:
        num = re.match(r"^\w+ (?P<num>\d+)$", query.data).group('num')
        return get_notification(context.bot_data['db_session'], int(num), chat_id)
    except (LookupError, ValueError):
        await query.edit_message_text('Не верный формат num')
    except NoResultFound:
        await query.edit_message_text('Напоминание не найдено.')


async def get_history_from_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> History:
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    try:
        num = re.match(r"^\w+ (?P<num>\d+)$", query.data).group('num')
        return get_history_row(context.bot_data['db_session'], int(num), chat_id)
    except (LookupError, ValueError):
        await query.edit_message_text('Не верный формат num')
    except NoResultFound:
        await query.edit_message_text('Запись не найдена.')
