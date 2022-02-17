from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from db import add_notification, Notification
from commands.alert import alert
from utils import send_to_scheduler


PILLNAME, PILLDOSAGE, PILLTIME = range(3)


def new_command(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command'] = {}
    update.message.reply_text(
        'Скинь название таблеток.\nДля отмены используй /cancel.',
    )
    return PILLNAME


def set_pill_name(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command']['name'] = update.message.text
    update.message.reply_text(
        'В какой дозе нужно пить? (формат 25мг/0.25г)',
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
    send_to_scheduler(notification, context.job_queue, alert)

    update.message.reply_text('Напоминание добавлено, ждем-с...')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END