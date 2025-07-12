from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from db import transaction_handler
from commands.alert_command import alert
from models.notification import del_notifications, get_all_notifications, enable_notification, disable_notification
from utils.scheduler import send_to_scheduler, stop_to_scheduler
from utils.query import get_notification_from_query


OFF, ON, DELETE = 'off', 'on', 'delete_pill'


def notification_message(ntf) -> str:
    msg = f'Тебе нужно выпить {ntf.name} ({ntf.dosage}) в {ntf.time}'
    if ntf.date_start:
        msg += f' с {ntf.date_start}'
    if ntf.date_end:
        msg += f' по {ntf.date_end}'
    return msg


@transaction_handler
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notifications = get_all_notifications(context.bot_data['db_session'], update.message.chat_id)
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
        await update.message.reply_text(notification_message(ntf), reply_markup=InlineKeyboardMarkup([buttons]))


@transaction_handler
async def active_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notifications = get_all_notifications(context.bot_data['db_session'], update.message.chat_id, enabled=True)
    if not notifications:
        await update.message.reply_text('Активных напоминаний нет')
        return

    for ntf in notifications:
        await update.message.reply_text(notification_message(ntf), reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text='Отключить', callback_data=f'{OFF} {ntf.id}')
        ]]))


@transaction_handler
async def waiting_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notifications = get_all_notifications(context.bot_data['db_session'], update.message.chat_id, enabled=False)
    if not notifications:
        await update.message.reply_text('Ожидающих напоминаний нет')
        return

    for ntf in notifications:
        await update.message.reply_text(notification_message(ntf), reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text='Включить', callback_data=f'{ON} {ntf.id}')
        ]]))


@transaction_handler
async def mod_on_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notification = await get_notification_from_query(update, context)
    if not notification:
        return
    enable_notification(context.bot_data['db_session'], notification)

    send_to_scheduler(notification.setting, notification, context.job_queue, alert)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f'Напоминание {notification.name} ({notification.dosage}) добавлено.')


@transaction_handler
async def mod_off_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notification = await get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    disable_notification(context.bot_data['db_session'], notification)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f'Напоминание {notification.name} ({notification.dosage}) остановлено.')


@transaction_handler
async def delete_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notification = await get_notification_from_query(update, context)
    if not notification:
        return

    stop_to_scheduler(notification.id, context.job_queue)
    del_notifications(context.bot_data['db_session'], notification)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f'Напоминание {notification.name} ({notification.dosage}) удалено.')
