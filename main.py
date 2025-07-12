import logging
import config

from pytz import timezone
from datetime import datetime

from telegram import Update
from telegram.ext import Application

from commands.alert_command import alert, toggle_notifications
from db import DB
from handlers import handlers
from models.notification import get_active_notifications
from utils.scheduler import send_to_scheduler, send_to_scheduler_once, make_every_day_task


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(config, 'LOGLEVEL', logging.WARN),
    filename='TabletosBot.log',
)
logging.Formatter.converter = lambda *args: datetime.now(tz=timezone(config.TIMEZONE)).timetuple()
logger = logging.getLogger('TabletosBot')


def main() -> None:
    app = Application.builder().token(config.TOKEN).build()
    for handler in handlers:
        app.add_handler(handler)
    app.bot_data['logger'] = logger

    db = DB(config.DB_PATH)
    app.bot_data['db'] = db

    now = datetime.now()
    with db.get_session() as db_session:
        for ntf in get_active_notifications(db_session, config.TIMEZONE):
            send_to_scheduler(ntf.setting, ntf, app.job_queue, alert)
            if ntf.next_t and ntf.next_t > now:
                send_to_scheduler_once(ntf.setting, ntf, app.job_queue, alert, ntf.next_t - now)

    time = datetime.strptime('00:00', '%H:%M').time()
    time = time.replace(tzinfo=timezone(config.TIMEZONE))
    make_every_day_task(time, app.job_queue, toggle_notifications)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
