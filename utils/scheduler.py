import datetime
import pytz

from telegram.ext import JobQueue

from models.notification import Notification
from models.setting import Setting


def send_to_scheduler(setting: Setting, notification: Notification, job_queue: JobQueue, callback):
    time = datetime.datetime.strptime(notification.time, '%H:%M').time()
    time = time.replace(tzinfo=pytz.timezone(setting.timezone))
    job_queue.run_daily(
        callback=callback, time=time, name=f'{notification.id} daily',
        context={'notification': notification, 'setting': setting},
    )


def send_to_scheduler_once(setting: Setting, notification: Notification, job_queue: JobQueue, callback):
    job_queue.run_once(
        callback, datetime.timedelta(minutes=setting.interval_alert), name=f'{notification.id} once',
        context={'notification': notification, 'setting': setting},
    )


def stop_to_scheduler_once(nid: int, job_queue: JobQueue):
    for job in job_queue.get_jobs_by_name(f'{nid} once'):
        job.schedule_removal()


def stop_to_scheduler(nid: int, job_queue: JobQueue):
    for job in job_queue.get_jobs_by_name(f'{nid} daily'):
        job.schedule_removal()
    for job in job_queue.get_jobs_by_name(f'{nid} once'):
        job.schedule_removal()
