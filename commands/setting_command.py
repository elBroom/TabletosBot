from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from models.setting import add_setting, Setting
from utils.user_data import set_setting


LANGUAGE, TIMEZONE, EMAIL, INTERVAL, PHOTO, URGENCY = range(6)
YES = ('да', 'д', 'yes', 'y')
NO = ('нет', 'н', 'now', 'n')

markup_bool = ReplyKeyboardMarkup([['да', 'нет']], one_time_keyboard=True)
markup_skip = ReplyKeyboardMarkup([['пропустить']], one_time_keyboard=True)


def setting_command(update: Update, context: CallbackContext) -> int:
    context.user_data['setting_command'] = {}
    update.message.reply_text('Давай настроимся на одну волну\nДля отмены используй /cancel.')
    update.message.reply_text(
        'Введи свою timizone в формате Europe/Moscow или пропусти для установки времени по Москве',
        reply_markup=markup_skip,
    )
    return TIMEZONE


def skip_timezone(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Что бы отправлять дневник выпитых таблеток, введи свой email',
        reply_markup=markup_skip,
    )
    return EMAIL


def set_timezone(update: Update, context: CallbackContext) -> int:
    context.user_data['setting_command']['timezone'] = update.message.text
    return skip_timezone(update, context)


def skip_email(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Если вдруг ты был занят, через сколько минут напомнить снова выпить таблетки?',
        reply_markup=ReplyKeyboardMarkup([[10, 15, 20, 30]], one_time_keyboard=True),
    )
    return INTERVAL


def set_email(update: Update, context: CallbackContext) -> int:
    context.user_data['setting_command']['email'] = update.message.text
    return skip_email(update, context)


def set_interval(update: Update, context: CallbackContext) -> int:
    context.user_data['setting_command']['interval'] = update.message.text
    update.message.reply_text(
        'После каждой принятой таблетки я могу спрашивать фото, нннадо?',
        reply_markup=markup_bool,
    )
    return PHOTO


def set_photo(update: Update, context: CallbackContext) -> int:
    take_photo = False
    if update.message.text in YES:
        take_photo = True
    context.user_data['setting_command']['photo'] = take_photo
    update.message.reply_text(
        'Я могу быть настойчивым и отправлять напоминания пока ты не выпьешь таблетки, тебе интересно?',
        reply_markup=markup_bool,
    )
    return URGENCY


def set_urgency(update: Update, context: CallbackContext) -> int:
    urgency_enabled = False
    if update.message.text in YES:
        urgency_enabled = True
    user_data = context.user_data['setting_command']

    setting = Setting(
        chat_id=update.message.chat_id,
        username=update.message.chat.username,
        timezone=user_data.get('timezone', 'Europe/Moscow'),
        email=user_data.get('email', ''),
        interval_alert=int(user_data.get('interval_alert', 20)),
        take_photo=bool(user_data.get('photo', False)),
        urgency_enabled=urgency_enabled,
    )
    add_setting(context.bot_data['db_session'], setting)
    set_setting(context, setting)
    update.message.reply_text('Настройки применены')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END
