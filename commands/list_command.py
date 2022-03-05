from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from commands.alert_command import alert
from models.notification import del_notifications, get_notifications, enable_notification, disable_notification
from utils.scheduler import send_to_scheduler, stop_to_scheduler
from utils.query import get_notification_from_query
from utils.user_data import get_setting


OFF, ON, DELETE = 'off', 'on', 'delete_pill'


def list_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    notifications = get_notifications(context.bot_data['db'], chat_id)
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
        update.message.reply_text(
            f'Тебе нужно выпить {ntf.name} ({ntf.dosage}) в {ntf.time}',
            reply_markup=InlineKeyboardMarkup([buttons]),
        )


def mod_on_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return
    enable_notification(context.bot_data['db'], notification)

    setting = get_setting(context, notification.chat_id)
    send_to_scheduler(setting, notification, context.job_queue, alert)

    query = update.callback_query
    query.message.reply_text('Напоминание добавлено.')


def mod_off_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    disable_notification(context.bot_data['db'], notification)

    query = update.callback_query
    query.message.reply_text('Напоминание остановлено.')


def delete_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    del_notifications(context.bot_data['db'], notification)

    query = update.callback_query
    query.message.reply_text('Напоминание удалено.')
