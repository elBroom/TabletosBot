import pytz

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from answers import YES, markup_bool, markup_skip
from db import transaction_handler
from models.setting import add_setting, get_setting


LANGUAGE, TIMEZONE, EMAIL, INTERVAL, URGENCY = range(5)


async def setting_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['setting_command'] = {}
    await update.message.reply_text('Давай настроимся на одну волну\nДля отмены используй /cancel.')
    await update.message.reply_text(
        'Введи свою timizone в формате Europe/Moscow.\n'
        'Так же можешь прислать свою локацию.\n'
        'Или пропусти шаг, тогда время будет московским.',
        reply_markup=markup_skip,
    )
    return TIMEZONE


async def skip_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Если вдруг ты был занят, через сколько минут напомнить снова выпить таблетки?',
        reply_markup=ReplyKeyboardMarkup([["10", "15", "20", "30", "40", "50"]], one_time_keyboard=True),
    )
    return INTERVAL


async def set_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        pytz.timezone(update.message.text)
    except pytz.exceptions.UnknownTimeZoneError:
        await update.message.reply_text('Не читаемый регион, давай еще раз')
        return TIMEZONE

    context.user_data['setting_command']['timezone'] = update.message.text
    return await skip_timezone(update, context)


async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        interval = int(update.message.text)
    except ValueError:
        await update.message.reply_text('Не похоже на число, давай еще раз')
        return TIMEZONE
    if interval < 1 or interval > 300:
        await update.message.reply_text('Давай установим разумное время')
        return TIMEZONE

    context.user_data['setting_command']['interval_alert'] = interval
    await update.message.reply_text(
        'Я могу быть настойчивым и отправлять напоминания пока ты не выпьешь таблетки, тебе интересно?',
        reply_markup=markup_bool,
    )
    return URGENCY


@transaction_handler
async def set_urgency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    urgency_enabled = False
    if update.message.text in YES:
        urgency_enabled = True
    user_data = context.user_data['setting_command']

    setting = get_setting(context.bot_data['db_session'], update.message.chat_id)
    if 'timezone' in user_data:
        setting.timezone = user_data['timezone']
    if 'interval_alert' in user_data:
        setting.interval_alert = user_data['interval_alert']
    setting.urgency_enabled = urgency_enabled

    context.bot_data['logger'].info(f'Add setting for chat_id: {setting.chat_id}')
    add_setting(context.bot_data['db_session'], setting)

    await update.message.reply_text('Настройки применены')
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END
