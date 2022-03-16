from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from db import transaction_handler
from commands.alert_command import alert
from models.notification import del_notifications, get_all_notifications, enable_notification, disable_notification
from utils.scheduler import send_to_scheduler, stop_to_scheduler
from utils.query import get_notification_from_query


OFF, ON, DELETE = 'off', 'on', 'delete_pill'


@transaction_handler
def list_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    notifications = get_all_notifications(context.chat_data['db_session'], chat_id)
    if not notifications:
        update.message.reply_text('Пока ничего нет')
        return

    for ntf in notifications:
        buttons = []
        if ntf.enabled:
            buttons.append(
                InlineKeyboardButton(text='Отключить', callback_data=f'{OFF} {ntf.id}')
            )
        else:
            buttons.append(
                InlineKeyboardButton(text='Включить', callback_data=f'{ON} {ntf.id}')
            )
        buttons.append(
            InlineKeyboardButton(text='Удалить', callback_data=f'{DELETE} {ntf.id}')
        )
        msg = f'Тебе нужно выпить {ntf.name} ({ntf.dosage}) в {ntf.time}'
        if ntf.date_start and ntf.date_end:
            msg += f' с {ntf.date_start} по {ntf.date_end}'
        update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup([buttons]))


@transaction_handler
def mod_on_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return
    enable_notification(context.chat_data['db_session'], notification)

    send_to_scheduler(notification.setting, notification, context.job_queue, alert)

    query = update.callback_query
    query.message.reply_text(f'Напоминание {notification.name} ({notification.dosage}) добавлено.')


@transaction_handler
def mod_off_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    disable_notification(context.chat_data['db_session'], notification)

    query = update.callback_query
    query.message.reply_text(f'Напоминание {notification.name} ({notification.dosage}) остановлено.')


@transaction_handler
def delete_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    del_notifications(context.chat_data['db_session'], notification)

    query = update.callback_query
    query.message.reply_text(f'Напоминание {notification.name} ({notification.dosage}) удалено.')
