import logging
import sentry_sdk
import config

from pytz import timezone
from datetime import datetime

from telegram.ext import Updater

from commands.alert_command import alert, toggle_notifications
from db import DB
from handlers import handlers
from models.notification import get_active_notifications
from utils.scheduler import send_to_scheduler, send_to_scheduler_once, make_every_day_task


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
    dispatcher.bot_data['db'] = db

    updater.job_queue.scheduler.start()
    now = datetime.now()
    with db.get_session() as db_session:
        for ntf in get_active_notifications(db_session, config.TIMEZONE):
            send_to_scheduler(ntf.setting, ntf, updater.job_queue, alert)
            if ntf.next_t and ntf.next_t > now:
                send_to_scheduler_once(ntf.setting, ntf, updater.job_queue, alert, ntf.next_t - now)

    time = datetime.strptime('00:00', '%H:%M').time()
    time = time.replace(tzinfo=timezone(config.TIMEZONE))
    make_every_day_task(time, updater.job_queue, toggle_notifications)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
