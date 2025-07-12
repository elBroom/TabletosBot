import os

from datetime import date, timedelta

from telegram import Update
from telegram.ext import ContextTypes


from db import transaction_handler
from models.history import get_history
from utils.report import make_csv_file


@transaction_handler
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    history = get_history(context.bot_data['db_session'], chat_id)
    if not history:
        await update.message.reply_text('Пока ничего нет')
        return

    filename = f'/tmp/report_{chat_id}.csv'
    make_csv_file(filename, history)

    context.bot_data['logger'].warn(f'Send report for chat_id: {chat_id}')
    await update.message.reply_document(document=open(filename, 'rb'), filename='report.csv')
    os.remove(filename)


@transaction_handler
async def report_last_quarter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    prev_month = date.today() - timedelta(days=92)
    history = get_history(context.bot_data['db_session'], chat_id, date=prev_month)
    if not history:
        await update.message.reply_text('Пока ничего нет')
        return

    filename = f'/tmp/report_{chat_id}.csv'
    make_csv_file(filename, history)

    context.bot_data['logger'].warn(f'Send report for chat_id: {chat_id}')
    await update.message.reply_document(document=open(filename, 'rb'), filename='report.csv')
    os.remove(filename)
