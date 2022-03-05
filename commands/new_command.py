from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from answers import TODAY, markup_today
from models.notification import add_notification, Notification
from commands.alert_command import alert
from utils.scheduler import send_to_scheduler
from utils.user_data import get_setting


NAME, DOSAGE, TIME, DATE_SET, DATE_START, DATE_END = range(6)


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
    context.user_data['new_command']['time'] = update.message.text
    update.message.reply_text(
        'Нужно ли установить дату начала и окончания приема?',
    )
    return DATE_SET


def data_setting(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Первый день приема таблеток? (формат 2022-12-01)',
        reply_markup=markup_today,
    )
    return DATE_START


def set_date_start(update: Update, context: CallbackContext) -> int:
    if update.message.text not in TODAY:
        context.user_data['new_command']['date_start'] = update.message.text
    update.message.reply_text(
        'Последний день приема таблеток? (формат 2022-12-01)',
        reply_markup=markup_today,
    )
    return DATE_END


def set_date_end(update: Update, context: CallbackContext) -> int:
    if update.message.text not in TODAY:
        context.user_data['new_command']['date_end'] = update.message.text
    return save_notification(update, context)


def save_notification(update: Update, context: CallbackContext) -> int:
    notification = Notification(
        chat_id=update.message.chat_id,
        name=context.user_data['new_command']['name'],
        dosage=context.user_data['new_command']['dosage'],
        time=context.user_data['new_command']['time'],
        date_start=context.user_data['new_command'].get('date_start', ''),
        date_end=context.user_data['new_command'].get('date_end', ''),
    )
    context.bot.logger.info(f'Add notification for chat_id: {notification.chat_id}')
    add_notification(context.bot_data['db'], notification)

    setting = get_setting(context, notification.chat_id)
    send_to_scheduler(setting, notification, context.job_queue, alert)

    update.message.reply_text(f'Напоминание {notification.name} ({notification.dosage}) добавлено, ждем-с...')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END
