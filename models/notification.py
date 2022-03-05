import datetime

from sqlalchemy import Boolean, Column, Integer, String, Date, DateTime, or_
from sqlalchemy.orm import Session

from db import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    name = Column(String)
    time = Column(String)
    dosage = Column(String)
    enabled = Column(Boolean, default=True)
    next_t = Column(DateTime)
    date_start = Column(Date)
    date_end = Column(Date)


def add_notification(session: Session, ntf: Notification):
    today = datetime.date.today()
    if ntf.date_start:
        ntf.date_start = datetime.datetime.strptime(ntf.date_start, '%Y-%m-%d').date()
    else:
        ntf.date_start = today

    if ntf.date_end:
        ntf.date_end = datetime.datetime.strptime(ntf.date_end, '%Y-%m-%d').date()
    else:
        ntf.date_end = today

    session.add(ntf)
    session.commit()
    return ntf.id


def get_active_notifications(session: Session):
    today = datetime.date.today()
    qs = session.query(Notification).order_by(Notification.time)
    qs = qs.filter_by(enabled=True)
    qs = qs.filter(or_(Notification.date_start == None, Notification.date_start <= today))
    qs = qs.filter(or_(Notification.date_end == None, Notification.date_end >= today))
    return qs.all()


def get_all_notifications(session: Session, chat_id=None):
    qs = session.query(Notification).order_by(Notification.time)
    if chat_id:
        qs = qs.filter_by(chat_id=chat_id)
    return qs.all()


def get_new_notifications(session: Session):
    today = datetime.date.today()
    qs = session.query(Notification).order_by(Notification.time)
    qs = qs.filter_by(enabled=True).filter_by(date_start=today)
    return qs.all()


def get_notification(session: Session, nid: int, chat_id: int):
    return session.query(Notification).filter_by(id=nid, chat_id=chat_id).one()


def enable_notification(session: Session, ntf: Notification):
    ntf.enabled = True
    session.commit()


def disable_notification(session: Session, ntf: Notification):
    ntf.enabled = False
    session.commit()


def del_notifications(session: Session, ntf: Notification):
    session.delete(ntf)
    session.commit()


def set_next_notification(session: Session, ntf: Notification, time: 'datetime'):
    ntf.next_t = time
    session.commit()
