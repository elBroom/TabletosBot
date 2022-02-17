import datetime
import pytz

from telegram.ext import JobQueue

from models.notification import Notification


def send_to_scheduler(notification: Notification, job_queue: JobQueue, callback):
    time = datetime.datetime.strptime(notification.time, '%H:%M').time()
    # TODO get timezone from DB
    time = time.replace(tzinfo=pytz.timezone('Europe/Moscow'))
    job_queue.run_daily(
        callback=callback, time=time, name=f'{notification.id} daily', context=notification,
    )


def send_to_scheduler_once(notification: Notification, job_queue: JobQueue, callback):
    # TODO get timezone from DB
    interval = 5

    job_queue.run_once(
        callback, datetime.timedelta(minutes=interval),
        name=f'{notification.id} once', context=notification,
    )


def stop_to_scheduler_once(nid: int, job_queue: JobQueue):
    for job in job_queue.get_jobs_by_name(f'{nid} once'):
        job.schedule_removal()


def stop_to_scheduler(nid: int, job_queue: JobQueue):
    for job in job_queue.get_jobs_by_name(f'{nid} daily'):
        job.schedule_removal()
    for job in job_queue.get_jobs_by_name(f'{nid} once'):
        job.schedule_removal()
