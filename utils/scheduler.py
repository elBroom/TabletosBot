import datetime
import pytz

from telegram.ext import JobQueue, Job

from models.notification import Notification
from models.setting import Setting


def remove_old_notification(job_queue: JobQueue):
    for job in job_queue.jobs():
        if 'daily' not in job.name:
            continue

        notification = job.context['notification']
        today = datetime.date.today()

        if notification.date_end and notification.date_end < today:
            job.schedule_removal()
            yield notification


def make_every_day_task(time: datetime.time, job_queue: JobQueue, callback):
    job_queue.run_daily(callback=callback, time=time, name='every day task')


def send_to_scheduler(setting: Setting, notification: Notification, job_queue: JobQueue, callback):
    today = datetime.date.today()
    if (
        notification.date_start and notification.date_start > today or
        notification.date_end and notification.date_end < today
    ):
        return

    time = datetime.datetime.strptime(notification.time, '%H:%M').time()
    time = time.replace(tzinfo=pytz.timezone(setting.timezone))
    job_queue.run_daily(
        callback=callback, time=time, name=f'{notification.id} daily',
        context={'notification': notification, 'setting': setting},
    )


def send_to_scheduler_once(
    setting: Setting, notification: Notification, job_queue: JobQueue, callback, timedelta=None,
) -> Job:
    if not timedelta:
        timedelta = datetime.timedelta(minutes=setting.interval_alert)
    return job_queue.run_once(
        callback, timedelta, name=f'{notification.id} once',
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
