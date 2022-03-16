from telegram import Update
from telegram.ext import CallbackContext


def help_command(update: Update, context: CallbackContext) -> None:
    """
    /setcommands
    setting - Настроить бот
    list - Посмотреть все напоминания
    new - Добавить напоминания
    add - Добавить в журнал пропущенный прием таблеток
    history - Посмотреть историю приняты таблеток
    report - Получить историю приняты таблеток в виде csv файла
    stop - Остановить все напоминания
    clean - Удалить все напоминания
    """
    commands = [
        '/setting - Настроить бот',
        '/list - Посмотреть все напоминания',
        '/new - Добавить напоминания',
        '/add - Добавить в журнал пропущенный прием таблеток',
        '/history - Посмотреть историю приняты таблеток',
        '/report - Получить историю приняты таблеток в виде csv файла',
        '/stop - Остановить все напоминания',
        '/clean - Удалить все напоминания',
    ]
    update.message.reply_text('\n'.join(commands))
