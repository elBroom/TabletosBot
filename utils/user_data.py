from telegram.ext import CallbackContext

from models.setting import Setting, get_setting as get_setting_db


def set_setting(context: CallbackContext, setting: Setting):
    context.user_data['setting'] = setting


def get_setting(context: CallbackContext, chat_id: int) -> Setting:
    if 'setting' not in context.user_data:
        setting = get_setting_db(context.chat_data['db_session'], chat_id)
        context.user_data['setting'] = setting
    return context.user_data['setting']
