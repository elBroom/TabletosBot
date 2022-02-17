import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, Message
from telegram.ext import CallbackContext, ConversationHandler

from db import (
    add_notification, del_notifications, get_notifications, get_notification, enable_notification, disable_notification,
    Notification, NoResultFound
)
from datatype import PILLNAME, PILLDOSAGE, PILLTIME, LISTBUTTON
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


def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет, давай знакомится. Для начала настрой меня /setting.')


def setting_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Напоминание остановлены.')


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Пидоры, помогите!')


def list_command(update: Update, context: CallbackContext) -> int:
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
    return LISTBUTTON


def clean_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    for ntf in get_notifications(context.bot_data['db_session'], chat_id):
        stop_to_scheduler(ntf.id, context.job_queue)
        del_notifications(context.bot_data['db_session'], ntf)

    update.message.reply_text('Добавь новое напоминание /new.')


def mod_on_query(update: Update, context: CallbackContext) -> None:
    notification = __get_notification(update, context)
    if not notification:
        return ConversationHandler.END

    enable_notification(context.bot_data['db_session'], notification)
    send_to_scheduler(notification, context.job_queue, alarm)

    query = update.callback_query
    query.answer()
    query.message.reply_text('Напоминание добавлено.')
    return ConversationHandler.END


def mod_off_query(update: Update, context: CallbackContext) -> int:
    notification = __get_notification(update, context)
    if not notification:
        return ConversationHandler.END

    stop_to_scheduler(notification.id, context.job_queue)
    disable_notification(context.bot_data['db_session'], notification)

    query = update.callback_query
    query.answer()
    query.message.reply_text('Напоминание остановлено.')
    return ConversationHandler.END


def delete_query(update: Update, context: CallbackContext) -> int:
    notification = __get_notification(update, context)
    if not notification:
        return ConversationHandler.END

    stop_to_scheduler(notification.id, context.job_queue)
    del_notifications(context.bot_data['db_session'], notification)

    query = update.callback_query
    query.answer()
    query.message.reply_text('Напоминание удалено.')
    return ConversationHandler.END


def stop_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    for ntf in get_notifications(context.bot_data['db_session'], chat_id):
        disable_notification(context.bot_data['db_session'], ntf)
        stop_to_scheduler(ntf.id, context.job_queue)

    update.message.reply_text('Напоминание остановлены.')


def new_command(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command'] = {}
    update.message.reply_text(
        'Скинь название таблеток.\nДля отмены используй /cancel.',
    )
    return PILLNAME


def set_pill_name(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command']['name'] = update.message.text
    update.message.reply_text(
        'В какой дозе нужно пить? (формат 0.25mg/1g)',
    )
    return PILLDOSAGE


def set_pill_dosage(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command']['dosage'] = update.message.text
    update.message.reply_text(
        'В какое время тебе напомнить? (формат 15:30)',
    )
    return PILLTIME


def set_pill_time(update: Update, context: CallbackContext) -> int:
    notification = Notification(
        chat_id=update.message.chat_id,
        name=context.user_data['new_command']['name'],
        dosage=context.user_data['new_command']['dosage'],
        time=update.message.text,
    )
    add_notification(context.bot_data['db_session'], notification)
    send_to_scheduler(notification, context.job_queue, alarm)

    update.message.reply_text('Напоминание добавлено, ждем-с...')
    return ConversationHandler.END


def alarm(context: CallbackContext) -> None:
    notification = context.job.context
    context.bot.send_message(
        notification.chat_id,
        text=f"Тэкс, тебе надо выпить таблетки {notification.name} ({notification.dosage}).",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text='Выпил', callback_data=f'take {notification.id}'),
            InlineKeyboardButton(text='Отложить', callback_data=f'postpound {notification.id}'),
        ]]),
    )


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END
