import os

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, ConversationHandler

from models.history import add_history
from utils.img import valid_img
from utils.scheduler import send_to_scheduler_once, stop_to_scheduler_once
from utils.query import get_notification_from_query
from utils.user_data import get_setting

TAKE, TAKEPHOTO, FORGOT, LATER = 'take', 'take_photo', 'forgot', 'later'
CHECK, SAVE = range(2)


def alert(context: CallbackContext) -> None:
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
        send_to_scheduler_once(setting, notification, context.job_queue, alert)
        buttons.append(
            InlineKeyboardButton(text='Забыл', callback_data=f'{FORGOT} {notification.id}'),
        )
    else:
        buttons.append(
            InlineKeyboardButton(text='Отложить', callback_data=f'{LATER} {notification.id}'),
        )

    context.bot.send_message(
        notification.chat_id,
        text=f"Тэкс, тебе надо выпить таблетки {notification.name} ({notification.dosage}).",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


def take_query(update: Update, context: CallbackContext) -> None:
    notification = get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler_once(notification.id, context.job_queue)
    setting = get_setting(context, notification.chat_id)
    add_history(context.bot_data['db_session'], notification, setting.timezone)

    query = update.callback_query
    query.message.reply_text('Запись добавлена в дневник.')


def take_photo_query(update: Update, context: CallbackContext) -> int:
    notification = get_notification_from_query(update, context)
    if not notification:
        return ConversationHandler.END

    context.user_data['take_photo_query'] = notification
    query = update.callback_query
    query.message.reply_text('Пришли фото')
    return CHECK


def check_photo(update: Update, context: CallbackContext) -> int:
    photo_file = update.message.photo[-1].get_file()
    file = photo_file.download()
    if not valid_img(file):
        update.message.reply_text('Не похоже это на фото')
        os.remove(file)
        return CHECK

    notification = context.user_data['take_photo_query']
    stop_to_scheduler_once(notification.id, context.job_queue)
    setting = get_setting(context, notification.chat_id)
    add_history(context.bot_data['db_session'], notification, setting.timezone)

    os.remove(file)
    update.message.reply_text('Запись добавлена в дневник.')
    return ConversationHandler.END


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

    setting = get_setting(context, notification.chat_id)
    send_to_scheduler_once(setting, notification, context.job_queue, alert)

    query = update.callback_query
    query.message.reply_text('Напоминание перенесено.')
