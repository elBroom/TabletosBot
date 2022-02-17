import logging

import config

from telegram.ext import Updater

from commands.alert import alert
from db import DB, get_notifications
from handlers import handlers
from utils import send_to_scheduler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    updater = Updater(config.TOKEN)

    dispatcher = updater.dispatcher
    for handler in handlers:
        dispatcher.add_handler(handler)

    db = DB(config.DB_PATH)
    dispatcher.bot_data['db_session'] = db.session

    updater.job_queue.scheduler.start()
    for ntf in get_notifications(db.session):
        if ntf.enabled:
            send_to_scheduler(ntf, updater.job_queue, alert)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
