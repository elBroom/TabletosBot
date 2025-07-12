from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        '/list_active - Посмотреть активные напоминания',
        '/list_waiting - Посмотреть не активные напоминания',
        '/new - Добавить напоминания',
        '/add - Добавить в журнал пропущенный прием таблеток',
        '/history - Посмотреть историю приняты таблеток',
        '/report - Получить историю приняты таблеток в виде csv файла',
        '/report_quarter - Получить историю за последний квартал',
        '/stop - Остановить все напоминания',
        '/clean - Удалить все напоминания',
    ]
    await update.effective_message.reply_text('\n'.join(commands))
