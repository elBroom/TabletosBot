import os

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, ConversationHandler

from answers import markup_skip
from db import transaction_handler
from models.notification import Notification, get_new_notifications, set_next_notification
from models.history import add_history
from utils.img import valid_img
from utils.scheduler import del_old_notification, send_to_scheduler, send_to_scheduler_once, stop_to_scheduler_once
from utils.query import get_notification_from_query
from utils.user_data import get_setting

TAKE, TAKEPHOTO, FORGOT, LATER = 'take', 'take_photo', 'forgot', 'later'
CHECK, SAVE = range(2)
HISTORY_SAVED = 'Запись {notification.name} ({notification.dosage}) добавлена в дневник.'


def toggle_notifications(context: CallbackContext) -> None:
    with context.bot_data['db'].get_session() as db_session:
        del_old_notification(db_session, context.job_queue)
        for ntf in get_new_notifications(db_session):
            send_to_scheduler(ntf.setting, ntf, context.job_queue, alert)


def alert(context: CallbackContext) -> None:
    context.bot.logger.info(f'Alert {context.job.name}')
    notification = context.job.context['notification']
    setting = context.job.context['setting']

    buttons = []
    if setting.take_photo:
        buttons.append(
            InlineKeyboardButton(text='Выпил', callback_data=f'{TAKEPHOTO} {notification.id}'),
        )
    else:
        buttons.append(
            InlineKeyboardButton(text='Выпил', callback_data=f'{TAKE} {notification.id}'),
        )

    if setting.urgency_enabled:
        job = send_to_scheduler_once(setting, notification, context.job_queue, alert)
        with context.bot_data['db'].get_session() as db_session:
            set_next_notification(db_session, notification, job.next_t)
        buttons.append(
            InlineKeyboardButton(text='Забыл', callback_data=f'{FORGOT} {notification.id}'),
        )
    else:
        buttons.append(
            InlineKeyboardButton(text='Отложить', callback_data=f'{LATER} {notification.id}'),
        )

    context.bot.logger.info(f'Send notification for chat_id: {notification.chat_id}')
    context.bot.send_message(
        notification.chat_id,
        text=f"Тэкс, тебе надо выпить таблетки {notification.name} ({notification.dosage}).",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


def save_history(context: CallbackContext, notification: Notification):
    stop_to_scheduler_once(notification.id, context.job_queue)
    setting = get_setting(context, notification.chat_id)
    context.bot.logger.info(f'Add row to history for chat_id: {setting.chat_id}')
    add_history(context.bot_data['db_session'], notification, setting.timezone)


@transaction_handler
def take_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    save_history(context, notification)
    query = update.callback_query
    query.message.reply_text(HISTORY_SAVED.format(notification=notification))


@transaction_handler
def take_photo_query(update: Update, context: CallbackContext) -> int:
    notification = get_notification_from_query(update, context)
    if not notification:
        return ConversationHandler.END

    context.user_data['take_photo_query'] = notification
    query = update.callback_query
    query.message.reply_text('Пришли фото', reply_markup=markup_skip)
    return CHECK


@transaction_handler
def check_photo(update: Update, context: CallbackContext) -> int:
    photo_file = update.message.photo[-1].get_file()
    file = photo_file.download()
    if not valid_img(file):
        update.message.reply_text('Не похоже это на фото')
        os.remove(file)
        return CHECK

    notification = context.user_data['take_photo_query']
    save_history(context, notification)

    os.remove(file)
    update.message.reply_text(HISTORY_SAVED.format(notification=notification))
    return ConversationHandler.END


@transaction_handler
def skip_photo(update: Update, context: CallbackContext) -> int:
    notification = context.user_data['take_photo_query']
    save_history(context, notification)

    update.message.reply_text(HISTORY_SAVED.format(notification=notification))
    return ConversationHandler.END


@transaction_handler
def forgot_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler_once(notification.id, context.job_queue)

    query = update.callback_query
    query.message.reply_text('Печально.')


@transaction_handler
def later_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    setting = get_setting(context, notification.chat_id)
    job = send_to_scheduler_once(setting, notification, context.job_queue, alert)
    set_next_notification(context.bot_data['db_session'], notification, job.next_t)

    context.bot.logger.info(f'Notification delayed for chat_id: {notification.chat_id}')
    query = update.callback_query
    query.message.reply_text(f'Напоминание перенесено на {setting.interval_alert} минут.')
