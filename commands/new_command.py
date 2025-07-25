from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from answers import TODAY, NO, MEASURING_RUS, SKIP, markup_today, markup_bool
from db import transaction_handler
from models.notification import add_notification, Notification
from models.setting import get_setting
from commands.alert_command import alert
from utils.scheduler import send_to_scheduler


NAME, DOSAGE, TIME, DATE_SET, DATE_START, DATE_END = range(6)


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_command'] = {}
    await update.message.reply_text(
        'Скинь название таблеток.\nДля отмены используй /cancel.',
    )
    return NAME


async def set_pill_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_command']['name'] = update.message.text
    await update.message.reply_text(
        f'В какой дозе нужно пить?\n(формат 0.25{"/".join(MEASURING_RUS)})',
    )
    return DOSAGE


async def set_pill_dosage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_command']['dosage'] = update.message.text
    await update.message.reply_text(
        'В какое время тебе напомнить? (формат 15:30)',
    )
    return TIME


async def set_pill_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_command']['time'] = update.message.text
    await update.message.reply_text(
        'Нужно ли установить дату начала и окончания приема?',
        reply_markup=markup_bool,
    )
    return DATE_SET


async def data_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in NO:
        return await save_notification(update, context)

    await update.message.reply_text(
        'Первый день приема таблеток? (формат 2025-12-01)',
        reply_markup=markup_today,
    )
    return DATE_START


async def set_date_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date = ''
    if update.message.text not in TODAY:
        date = update.message.text
    context.user_data['new_command']['date_start'] = date
    await update.message.reply_text(
        'Последний день приема таблеток? (формат 2025-12-01)',
        reply_markup=ReplyKeyboardMarkup([[TODAY[0], SKIP[0]]], one_time_keyboard=True)
    )
    return DATE_END


async def set_date_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in TODAY+SKIP:
        context.user_data['new_command']['date_end'] = update.message.text
    return await save_notification(update, context)


@transaction_handler
async def save_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    notification = Notification(
        chat_id=update.message.chat_id,
        name=context.user_data['new_command']['name'],
        dosage=context.user_data['new_command']['dosage'],
        time=context.user_data['new_command']['time'],
        date_start=context.user_data['new_command'].get('date_start'),
        date_end=context.user_data['new_command'].get('date_end'),
    )
    context.bot_data['logger'].info(f'Add notification for chat_id: {notification.chat_id}')

    setting = get_setting(context.bot_data['db_session'], notification.chat_id)
    add_notification(context.bot_data['db_session'], notification, setting.timezone)
    send_to_scheduler(setting, notification, context.job_queue, alert)

    await update.message.reply_text(f'Напоминание {notification.name} ({notification.dosage}) добавлено, ждем-с...')
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END
