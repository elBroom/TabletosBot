from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from models.notification import Notification
from models.history import add_history
from utils.user_data import get_setting


NAME, DOSAGE, TIME = range(3)


def add_command(update: Update, context: CallbackContext) -> int:
    context.user_data['add_command'] = {}
    update.message.reply_text(
        'Скинь название таблеток.\nДля отмены используй /cancel.',
    )
    return NAME


def set_pill_name(update: Update, context: CallbackContext) -> int:
    context.user_data['add_command']['name'] = update.message.text
    update.message.reply_text(
        'Какую дозу выпил? (формат 25мг/0.25г)',
    )
    return DOSAGE


def set_pill_dosage(update: Update, context: CallbackContext) -> int:
    context.user_data['add_command']['dosage'] = update.message.text
    update.message.reply_text(
        'В какое время выпил таблетку? (формат 2021-12-01 15:30)',
        reply_markup=ReplyKeyboardMarkup([['сейчас']], one_time_keyboard=True),
    )
    return TIME


def set_pill_time(update: Update, context: CallbackContext) -> int:
    notification = Notification(
        chat_id=update.message.chat_id,
        name=context.user_data['add_command']['name'],
        dosage=context.user_data['add_command']['dosage'],
    )
    context.bot.logger.info(f'Add history for chat_id: {notification.chat_id}')
    setting = get_setting(context, notification.chat_id)

    time = update.message.text
    if update.message.text in ('сейчас', 'now'):
        time = ''

    add_history(context.bot_data['db_session'], notification, setting.timezone, time=time)

    update.message.reply_text(f'Запись {notification.name} ({notification.dosage}) добавлена.')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END
