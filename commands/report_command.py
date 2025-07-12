import csv
import os

from telegram import Update
from telegram.ext import ContextTypes
from transliterate import translit

from db import transaction_handler
from models.history import get_history


@transaction_handler
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    history = get_history(context.bot_data['db_session'], chat_id)
    if not history:
        await update.message.reply_text('Пока ничего нет')
        return

    filename = f'/tmp/report_{chat_id}.csv'
    with open(filename, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'name', 'dosage'])
        for hst in history:
            writer.writerow(list(convert_data([hst.datetime, hst.name, hst.dosage.replace(',', '.')])))

    context.bot_data['logger'].warn(f'Send report for chat_id: {chat_id}')
    await update.message.reply_document(document=open(filename, 'rb'), filename='report.csv')
    os.remove(filename)


def convert_data(data: list):
    for row in data:
        yield translit(row, 'ru', reversed=True)
