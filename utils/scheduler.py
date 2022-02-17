import datetime
import pytz

from telegram.ext import JobQueue

from models.notification import Notification


def send_to_scheduler(notification: Notification, job_queue: JobQueue, callback):
    time = datetime.datetime.strptime(notification.time, '%H:%M').time()
    # TODO get timezone from DB
    time = time.replace(tzinfo=pytz.timezone('Europe/Moscow'))
    job_queue.run_daily(
        callback=callback, time=time, name=str(notification.id), context=notification,
    )


def send_to_scheduler_once(notification: Notification, job_queue: JobQueue, callback):
    # TODO get timezone from DB
    interval = 5

    job_queue.run_once(
        callback, datetime.timedelta(minutes=interval),
        name=str(notification.id), context=notification,
    )


def stop_to_scheduler(nid: int, job_queue: JobQueue):
    for job in job_queue.get_jobs_by_name(str(nid)):
        job.schedule_removal()
