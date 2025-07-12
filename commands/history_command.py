from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from db import transaction_handler
from models.history import del_history_row, get_history
from utils.query import get_history_from_query


DELETE = 'delete_log'
LIMIT = 3


@transaction_handler
async def history_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    history = get_history(context.bot_data['db_session'], chat_id)
    if not history:
        await update.effective_message.reply_text('Пока ничего нет')
        return

    for hst in history[len(history) - LIMIT:]:
        await update.effective_message.reply_text(
            text=f'Ты выпил {hst.name} ({hst.dosage}) в {hst.datetime}',
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(text='Удалить', callback_data=f'{DELETE} {hst.id}'),
                ]
            ]),
        )


@transaction_handler
async def delete_log_query(update: Update, context: CallbackContext) -> None:
    history = await get_history_from_query(update, context)
    if not history:
        return

    del_history_row(context.bot_data['db_session'], history)

    await update.callback_query.edit_message_text(f'Запись {history.name} ({history.dosage}) удалена.')
