import config

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from db import transaction_handler
from models.notification import (
    Notification, disable_notification, get_new_notifications, get_notification, set_next_notification
)
from models.history import add_history
from utils.scheduler import remove_old_notification, send_to_scheduler, send_to_scheduler_once, stop_to_scheduler_once, stop_to_scheduler
from utils.query import get_notification_from_query


TAKE, FORGOT, LATER = 'take', 'forgot', 'later'
CHECK, SAVE = range(2)
HISTORY_SAVED = 'Запись {notification.name} ({notification.dosage}) добавлена в дневник.'


def toggle_notifications(context: ContextTypes.DEFAULT_TYPE) -> None:
    # TODO get timezone from settings
    timezone = config.TIMEZONE
    with context.bot_data['db'].get_session() as db_session:
        for ntf in remove_old_notification(context.job_queue, timezone):
            context.bot_data['logger'].info(f'Expire notification {ntf.id}')
            # TODO get all notifications
            notification = get_notification(db_session, ntf.id, ntf.chat_id)
            disable_notification(db_session, notification)
        for ntf in get_new_notifications(db_session, timezone):
            context.bot_data['logger'].info(f'Enable notification {ntf.id}')
            send_to_scheduler(ntf.setting, ntf, context.job_queue, alert)


async def alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.bot_data['logger'].info(f'Alert {context.job.name}')
    ntf = context.job.data['notification']
    with context.bot_data['db'].get_session() as db_session:
        notification = get_notification(db_session, ntf.id, ntf.chat_id)

        buttons = [
            InlineKeyboardButton(text='Выпил', callback_data=f'{TAKE} {notification.id}'),
        ]

        if notification.setting.urgency_enabled:
            job = send_to_scheduler_once(notification.setting, notification, context.job_queue, alert)

            set_next_notification(db_session, notification, job.next_t)
            buttons.append(
                InlineKeyboardButton(text='Забыл', callback_data=f'{FORGOT} {notification.id}'),
            )
        else:
            buttons.append(
                InlineKeyboardButton(text='Отложить', callback_data=f'{LATER} {notification.id}'),
            )

    context.bot_data['logger'].warn(f'Send notification for chat_id: {notification.chat_id}')
    await context.bot.send_message(
        notification.chat_id,
        text=f"Тэкс, тебе надо выпить таблетки {notification.name} ({notification.dosage}).",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


def save_history(context: ContextTypes.DEFAULT_TYPE, notification: Notification):
    stop_to_scheduler_once(notification.id, context.job_queue)
    context.bot_data['logger'].info(f'Add row to history for chat_id: {notification.chat_id}')
    add_history(context.bot_data['db_session'], notification, notification.setting.timezone)


@transaction_handler
async def take_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notification = await get_notification_from_query(update, context)
    if not notification:
        return

    save_history(context, notification)
    await update.callback_query.edit_message_text(HISTORY_SAVED.format(notification=notification))

@transaction_handler
async def forgot_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notification = await get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler_once(notification.id, context.job_queue)

    await update.callback_query.edit_message_text('Печально.')


@transaction_handler
async def later_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notification = await get_notification_from_query(update, context)
    if not notification:
        return

    job = send_to_scheduler_once(notification.setting, notification, context.job_queue, alert)
    set_next_notification(context.bot_data['db_session'], notification, job.next_t)

    context.bot_data['logger'].info(f'Notification delayed for chat_id: {notification.chat_id}')
    await update.callback_query.edit_message_text(f'Напоминание перенесено на {notification.setting.interval_alert} минут.')
