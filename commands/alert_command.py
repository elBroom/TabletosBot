from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from models.history import add_history
from utils.scheduler import send_to_scheduler_once, stop_to_scheduler_once
from utils.query import get_notification_from_query


TAKE, FORGOT, LATER  = 'take', 'forgot', 'later'


def alert(context: CallbackContext) -> None:
    notification = context.job.context
    context.bot.send_message(
        notification.chat_id,
        text=f"Тэкс, тебе надо выпить таблетки {notification.name} ({notification.dosage}).",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text='Выпил', callback_data=f'{TAKE} {notification.id}'),
                InlineKeyboardButton(text='Забыл', callback_data=f'{FORGOT} {notification.id}'),
            ]
        ]),
    )
    send_to_scheduler_once(notification, context.job_queue, alert)


def take_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler_once(notification.id, context.job_queue)
    add_history(context.bot_data['db_session'], notification)

    query = update.callback_query
    query.message.reply_text('Запись добавлена в дневник.')


def forgot_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler_once(notification.id, context.job_queue)

    query = update.callback_query
    query.message.reply_text('Печально.')


def later_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    send_to_scheduler_once(notification, context.job_queue, alert)

    query = update.callback_query
    query.message.reply_text('Напоминание перенесено.')
