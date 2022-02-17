from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext


def alert(context: CallbackContext) -> None:
    notification = context.job.context
    context.bot.send_message(
        notification.chat_id,
        text=f"Тэкс, тебе надо выпить таблетки {notification.name} ({notification.dosage}).",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text='Выпил', callback_data=f'take {notification.id}'),
                InlineKeyboardButton(text='Забыл', callback_data=f'take {notification.id}'),
            ],
            [
                InlineKeyboardButton(text='Отложить', callback_data=f'later {notification.id}'),
            ]
        ]),
    )

