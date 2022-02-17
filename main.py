import logging

import config

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from command import (
    start_command, help_command, list_command,
    setting_command, new_command,
    delete_query, clean_command,
    mod_on_query, mod_off_query, stop_command,
    set_pill_name, set_pill_dosage, set_pill_time, cancel, alarm,
)
from datatype import PILLNAME, PILLDOSAGE, PILLTIME, LISTBUTTON
from db import DB, get_notifications
from utils import send_to_scheduler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    updater = Updater(config.TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('setting', setting_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('clean', clean_command))
    dispatcher.add_handler(CommandHandler('stop', stop_command))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('new', new_command)],
        states={
            PILLNAME: [MessageHandler(Filters.regex('^[\w]+$'), set_pill_name)],
            PILLDOSAGE: [MessageHandler(Filters.regex('^[0-9.,]+(мг|г|mg|g)$'), set_pill_dosage)],
            PILLTIME: [MessageHandler(Filters.regex('^[0-2][0-9]:[0-6][0-9]$'), set_pill_time)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('list', list_command)],
        states={
            LISTBUTTON: [
                CallbackQueryHandler(mod_on_query, pattern='^on [0-9]+$'),
                CallbackQueryHandler(mod_off_query, pattern='^off [0-9]+$'),
                CallbackQueryHandler(delete_query, pattern='^delete [0-9]+$'),
            ],
        },
        fallbacks=[],
    ))

    db = DB(config.DB_PATH)
    dispatcher.bot_data['db_session'] = db.session

    updater.job_queue.scheduler.start()
    for ntf in get_notifications(db.session):
        if ntf.enabled:
            send_to_scheduler(ntf, updater.job_queue, alarm)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
