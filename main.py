import logging
import datetime
import pytz

import config

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, JobQueue

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

PILLNAME, PILLDOSAGE, PILLTIME = range(3)


def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome, try to add new pill via /new.')


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help me, please!')


def list_command(update: Update, context: CallbackContext) -> None:
    for ntf in config.NOTIFICATIONS:
        update.message.reply_text(f"You have to take {ntf['name']} ({ntf['dosage']}) pill at {ntf['time']}.")


def clean_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))

    for job in current_jobs:
        job.schedule_removal()

    update.message.reply_text('Welcome, try to add new pill via /new.')


def new_command(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command'] = {}
    update.message.reply_text(
        'Please, send me pill name.\nIf you want to cancel this operation type /cancel.',
    )
    return PILLNAME


def set_pill_name(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command']['name'] = update.message.text
    update.message.reply_text(
        'Send me the dosage of the next pill intake (like that 0.25mg).',
    )
    return PILLDOSAGE


def set_pill_dosage(update: Update, context: CallbackContext) -> int:
    context.user_data['new_command']['dosage'] = update.message.text
    update.message.reply_text(
        'Send me the time of the next pill intake (like that 15:30). After that you can add some more.',
    )
    return PILLTIME


def set_pill_time(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    context.user_data['new_command']['time'] = update.message.text
    send_to_scheduler(chat_id, context.user_data['new_command'], context.job_queue)
    config.NOTIFICATIONS.append(context.user_data['new_command'])
    update.message.reply_text(
        'Add more time for notifications or save this list.',
    )
    return ConversationHandler.END


def alarm(context: CallbackContext) -> None:
    job = context.job
    logger.info("Chat ids %d: %s", job.context, context.args)
    context.bot.send_message(job.context['chat_id'],
        text=f"You have to take {job.context['name']} ({job.context['dosage']}) pill at {job.context['time']}.")


def send_to_scheduler(chat_id: int, data: dict, job_queue: JobQueue):
    time = datetime.datetime.strptime(data['time'], '%H:%M').time()
    # TODO set custom timezone
    time = time.replace(tzinfo=pytz.timezone('Europe/Moscow'))
    job_queue.run_daily(
        callback=alarm, time=time, name=str(chat_id),
        context={
            'chat_id': chat_id,
            'name': data['name'],
            'dosage': data['dosage'],
            'time': data['time'],
        },
    )


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('State cancelled')
    return ConversationHandler.END


def main() -> None:
    updater = Updater(config.TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('list', list_command))
    dispatcher.add_handler(CommandHandler('clean', clean_command))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('new', new_command)],
        states={
            PILLNAME: [MessageHandler(Filters.regex('^[\w]+$'), set_pill_name)],
            PILLDOSAGE: [MessageHandler(Filters.regex('^[0-9.,]+(мг|г|mg|g)$'), set_pill_dosage)],
            PILLTIME: [MessageHandler(Filters.regex('^[0-2][0-9]:[0-6][0-9]$'), set_pill_time)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))

    for ntf in config.NOTIFICATIONS:
        send_to_scheduler(config.CHAT_ID, ntf, updater.job_queue)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()