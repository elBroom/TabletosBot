from telegram import Update
from telegram.ext import CallbackContext

from models.history import get_history


def history_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    history = get_history(context.bot_data['db_session'], chat_id)
    if not history:
        update.message.reply_text('Пока ничего нет')
        return

    for hst in history:
        update.message.reply_text(
            f'Ты выпил {hst.name} ({hst.dosage}) в {hst.created_at}',
        )
