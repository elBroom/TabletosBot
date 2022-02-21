import logging
import sentry_sdk
import config

from pytz import timezone
from datetime import datetime

from telegram.ext import Updater

from commands.alert_command import alert
from db import DB
from handlers import handlers
from models.notification import get_notifications
from models.setting import get_setting
from utils.scheduler import send_to_scheduler, send_to_scheduler_once


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='TabletosBot.log',
)
logging.Formatter.converter = lambda *args: datetime.now(tz=timezone(config.TIMEZONE)).timetuple()
logger = logging.getLogger(__name__)


def main() -> None:
    if config.SENTRY_DSN:
        sentry_sdk.init(config.SENTRY_DSN, traces_sample_rate=1.0)

    updater = Updater(config.TOKEN, workers=100)
    dispatcher = updater.dispatcher
    for handler in handlers:
        dispatcher.add_handler(handler)
    # dispatcher.add_error_handler(lambda *args: logger.info('Oops!'))

    db = DB(config.DB_PATH)
    dispatcher.bot_data['db_session'] = db.session

    updater.job_queue.scheduler.start()
    for ntf in get_notifications(db.session):
        if ntf.enabled:
            # TODO don't make query
            setting = get_setting(db.session, ntf.chat_id)
            send_to_scheduler(setting, ntf, updater.job_queue, alert)
            if ntf.next_t and ntf.next_t > datetime.now():
                send_to_scheduler_once(setting, ntf, updater.job_queue, alert, ntf.next_t - datetime.now())

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
