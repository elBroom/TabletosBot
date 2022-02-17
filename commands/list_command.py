import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from db import (
    del_notifications, get_notifications, get_notification, enable_notification, disable_notification,
    Notification, NoResultFound
)
from commands.alert_command import alert
from utils import send_to_scheduler, stop_to_scheduler


def __get_notification(update: Update, context: CallbackContext) -> Notification:
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    try:
        nid = re.match(r"^(on|off|delete) (?P<nid>\d+)$", query.data).group('nid')
        return get_notification(context.bot_data['db_session'], int(nid), chat_id)
    except (LookupError, ValueError):
        query.message.reply_text('Не верный формат num')
    except NoResultFound:
        query.message.reply_text('Напоминание не найдено.')


def list_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    for ntf in get_notifications(context.bot_data['db_session'], chat_id):
        buttons = []
        if ntf.enabled:
            buttons.append(
                InlineKeyboardButton(text='Отключить', callback_data=f'off {ntf.id}')
            )
        else:
            buttons.append(
                InlineKeyboardButton(text='Включить', callback_data=f'on {ntf.id}')
            )
        buttons.append(
            InlineKeyboardButton(text='Удалить', callback_data=f'delete {ntf.id}')
        )
        update.message.reply_text(
            f'Тебе нужно выпить {ntf.name} ({ntf.dosage}) в {ntf.time}',
            reply_markup=InlineKeyboardMarkup([buttons]),
        )


def mod_on_query(update: Update, context: CallbackContext) -> None:
    notification = __get_notification(update, context)
    if not notification:
        return

    enable_notification(context.bot_data['db_session'], notification)
    send_to_scheduler(notification, context.job_queue, alert)

    query = update.callback_query
    query.answer()
    query.message.reply_text('Напоминание добавлено.')


def mod_off_query(update: Update, context: CallbackContext) -> None:
    notification = __get_notification(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    disable_notification(context.bot_data['db_session'], notification)

    query = update.callback_query
    query.answer()
    query.message.reply_text('Напоминание остановлено.')


def delete_query(update: Update, context: CallbackContext) -> None:
    notification = __get_notification(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    del_notifications(context.bot_data['db_session'], notification)

    query = update.callback_query
    query.answer()
    query.message.reply_text('Напоминание удалено.')
    return
