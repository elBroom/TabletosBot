from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from db import add_notifications, del_notifications, get_notifications, get_notification, Notification, NoResultFound
from datatype import PILLNAME, PILLDOSAGE, PILLTIME
from utils import send_to_scheduler, stop_to_scheduler


def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет, добавь новое напоминание /new.')


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Пидоры, помогите!')


def list_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    for ntf in get_notifications(context.bot_data['db_session'], chat_id):
        update.message.reply_text(f'Тебе нужно выпить {ntf.name} ({ntf.dosage}) в {ntf.time}. [{ntf.id}]')
    update.message.reply_text(f'Для удаления используй /delete num')


def delete_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        nid = int(context.args[0])
    except (LookupError, ValueError):
        update.message.reply_text('Не верный формат num')
        return

    try:
        notification = get_notification(context.bot_data['db_session'], nid, chat_id)
    except NoResultFound:
        update.message.reply_text('Напоминание не найдено.')
        return

    stop_to_scheduler(notification.id, context.job_queue)
    del_notifications(context.bot_data['db_session'], notification)
    update.message.reply_text('Напоминание удалено.')


def clean_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    for ntf in get_notifications(context.bot_data['db_session'], chat_id):
        stop_to_scheduler(ntf.id, context.job_queue)
        del_notifications(context.bot_data['db_session'], ntf)

    update.message.reply_text('Добавь новое напоминание /new.')


def stop_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        nid = int(context.args[0])
    except (LookupError, ValueError):
        update.message.reply_text('Не верный формат num')
        return

    try:
        notification = get_notification(context.bot_data['db_session'], nid, chat_id)
    except NoResultFound:
        update.message.reply_text('Напоминание не найдено.')
        return

    stop_to_scheduler(notification.id, context.job_queue)
    update.message.reply_text('Напоминание остановлено.')


def new_command(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command'] = {}
    update.message.reply_text(
        'Скинь название таблеток.\nДля отмены используй /cancel.',
    )
    return PILLNAME


def set_pill_name(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command']['name'] = update.message.text
    update.message.reply_text(
        'В какой дозе нужно пить? (формат 0.25mg/1g)',
    )
    return PILLDOSAGE


def set_pill_dosage(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command']['dosage'] = update.message.text
    update.message.reply_text(
        'В какое время тебе напомнить? (формат 15:30)',
    )
    return PILLTIME


def set_pill_time(update: Update, context: CallbackContext) -> int:
    notification = Notification(
        chat_id=update.message.chat_id,
        name=context.user_data['new_command']['name'],
        dosage=context.user_data['new_command']['dosage'],
        time=update.message.text,
    )
    add_notifications(context.bot_data['db_session'], notification)
    send_to_scheduler(notification, context.job_queue, alarm)

    update.message.reply_text('Напоминание добавлено, ждите...')
    return ConversationHandler.END


def alarm(context: CallbackContext) -> None:
    job = context.job
    context.bot.send_message(
        job.context['chat_id'],
        text=f"Тэкс, ты будешь пить {job.context['name']} ({job.context['dosage']}) в {job.context['time']} или как?",
    )


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('А все так хорошо начиналось...')
    return ConversationHandler.END
