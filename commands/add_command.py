from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from answers import NOW, MEASURING_RUS, markup_now
from db import transaction_handler
from models.notification import Notification
from models.history import add_history
from models.setting import get_setting


NAME, DOSAGE, TIME = range(3)


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['add_command'] = {}
    await update.message.reply_text(
        'Скинь название таблеток.\nДля отмены используй /cancel.',
    )
    return NAME


async def set_pill_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['add_command']['name'] = update.message.text
    await update.message.reply_text(
        f'Какую дозу выпил?\n(формат 25{"/".join(MEASURING_RUS)})',
    )
    return DOSAGE


async def set_pill_dosage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['add_command']['dosage'] = update.message.text
    await update.message.reply_text(
        'В какое время выпил таблетку? (формат 15:30/2022-12-01 15:30)',
        reply_markup=markup_now,
    )
    return TIME


@transaction_handler
async def set_pill_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    notification = Notification(
        chat_id=update.message.chat_id,
        name=context.user_data['add_command']['name'],
        dosage=context.user_data['add_command']['dosage'],
    )

    time = update.message.text
    if update.message.text in NOW:
        time = ''

    setting = get_setting(context.bot_data['db_session'], notification.chat_id)
    add_history(context.bot_data['db_session'], notification, setting.timezone, time=time)

    context.bot_data['logger'].info(f'Add history for chat_id: {notification.chat_id}')
    await update.message.reply_text(f'Запись {notification.name} ({notification.dosage}) добавлена.')
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END
