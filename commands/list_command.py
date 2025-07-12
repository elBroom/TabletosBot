from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, ContextTypes

from db import transaction_handler
from commands.alert_command import alert
from models.notification import del_notifications, get_all_notifications, enable_notification, disable_notification
from utils.scheduler import send_to_scheduler, stop_to_scheduler
from utils.query import get_notification_from_query


OFF, ON, DELETE = 'off', 'on', 'delete_pill'


@transaction_handler
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    notifications = get_all_notifications(context.bot_data['db_session'], chat_id)
    if not notifications:
        await update.message.reply_text('Пока ничего нет')
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
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup([buttons]))


@transaction_handler
async def mod_on_query(update: Update, context: CallbackContext) -> None:
    notification = await get_notification_from_query(update, context)
    if not notification:
        return
    enable_notification(context.bot_data['db_session'], notification)

    send_to_scheduler(notification.setting, notification, context.job_queue, alert)

    await update.callback_query.edit_message_text(f'Напоминание {notification.name} ({notification.dosage}) добавлено.')


@transaction_handler
async def mod_off_query(update: Update, context: CallbackContext) -> None:
    notification = await get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    disable_notification(context.bot_data['db_session'], notification)

    await update.callback_query.edit_message_text(f'Напоминание {notification.name} ({notification.dosage}) остановлено.')


@transaction_handler
async def delete_query(update: Update, context: CallbackContext) -> None:
    notification = await get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    del_notifications(context.bot_data['db_session'], notification)

    await update.callback_query.edit_message_text(f'Напоминание {notification.name} ({notification.dosage}) удалено.')
