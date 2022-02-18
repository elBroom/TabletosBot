from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from models.notification import add_notification, Notification
from commands.alert_command import alert
from utils.scheduler import send_to_scheduler
from utils.user_data import get_setting


NAME, DOSAGE, TIME = range(3)


def new_command(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command'] = {}
    update.message.reply_text(
        'Скинь название таблеток.\nДля отмены используй /cancel.',
    )
    return NAME


def set_pill_name(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command']['name'] = update.message.text
    update.message.reply_text(
        'В какой дозе нужно пить? (формат 25мг/0.25г)',
    )
    return DOSAGE


def set_pill_dosage(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command']['dosage'] = update.message.text
    update.message.reply_text(
        'В какое время тебе напомнить? (формат 15:30)',
    )
    return TIME


def set_pill_time(update: Update, context: CallbackContext) -> int:
    notification = Notification(
        chat_id=update.message.chat_id,
        name=context.user_data['new_command']['name'],
        dosage=context.user_data['new_command']['dosage'],
        time=update.message.text,
    )
    context.bot.logger.info(f'Add notification for chat_id: {notification.chat_id}')
    add_notification(context.bot_data['db_session'], notification)

    setting = get_setting(context, notification.chat_id)
    send_to_scheduler(setting, notification, context.job_queue, alert)

    update.message.reply_text('Напоминание добавлено, ждем-с...')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END
