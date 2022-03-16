import csv
import os

from telegram import Update
from telegram.ext import CallbackContext

from db import transaction_handler
from models.history import get_history


@transaction_handler
def report_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    history = get_history(context.chat_data['db_session'], chat_id)
    if not history:
        update.message.reply_text('Пока ничего нет')
        return

    filename = f'/tmp/report_{chat_id}.csv'
    with open(filename, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'name', 'dosage'])
        for hst in history:
            writer.writerow([hst.datetime, hst.name, hst.dosage.replace(',', '.')])

    context.bot.logger.info(f'Send report for chat_id: {chat_id}')
    update.message.reply_document(document=open(filename, 'rb'), filename='report.csv')
    os.remove(filename)
