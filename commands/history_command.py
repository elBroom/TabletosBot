from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from models.history import del_history_row, get_history
from utils.query import get_history_from_query


DELETE = 'delete_log'


def history_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    history = get_history(context.bot_data['db_session'], chat_id)
    if not history:
        update.message.reply_text('Пока ничего нет')
        return

    for hst in history:
        update.message.reply_text(
            text=f'Ты выпил {hst.name} ({hst.dosage}) в {hst.datetime}',
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(text='Удалить', callback_data=f'{DELETE} {hst.id}'),
                ]
            ]),
        )


def delete_log_query(update: Update, context: CallbackContext) -> None:
    history = get_history_from_query(update, context)
    if not history:
        return

    del_history_row(context.bot_data['db_session'], history)

    query = update.callback_query
    query.message.reply_text(f'Запись {history.name} ({history.dosage}) удалена.')
