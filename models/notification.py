import datetime

from sqlalchemy import Boolean, Column, Integer, String, Date, DateTime, or_

from db import Base, DB


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


def add_notification(engine: DB, ntf: Notification):
    today = datetime.date.today()
    if ntf.date_start:
        ntf.date_start = datetime.datetime.strptime(ntf.date_start, '%Y-%m-%d')
    else:
        ntf.date_start = today

    if ntf.date_end:
        ntf.date_end = datetime.datetime.strptime(ntf.date_end, '%Y-%m-%d')
    else:
        ntf.date_end = today

    with engine.get_session() as session:
        session.add(ntf)
        session.commit()
    return ntf.id


def get_active_notifications(engine: DB):
    today = datetime.date.today()
    with engine.get_session() as session:
        qs = session.query(Notification).order_by(Notification.time)
        qs = qs.filter_by(
            Notification.enabled is True,
            or_(Notification.date_start is None, Notification.date_start <= today),
            or_(Notification.date_end is None, Notification.date_end >= today),
        )
        return qs.all()


def get_all_notifications(engine: DB, chat_id=None):
    with engine.get_session() as session:
        qs = session.query(Notification).order_by(Notification.time)
        if chat_id:
            qs = qs.filter_by(chat_id=chat_id)
        return qs.all()


def get_new_notifications(engine: DB):
    today = datetime.date.today()
    with engine.get_session() as session:
        qs = session.query(Notification).order_by(Notification.time)
        qs = qs.filter_by(enabled=True).filter_by(date_start=today)
        return qs.all()


def get_notification(engine: DB, nid: int, chat_id: int):
    with engine.get_session() as session:
        return session.query(Notification).filter_by(id=nid, chat_id=chat_id).one()


def enable_notification(engine: DB, ntf: Notification):
    with engine.get_session() as session:
        ntf.enabled = True
        session.commit()


def disable_notification(engine: DB, ntf: Notification):
    with engine.get_session() as session:
        ntf.enabled = False
        session.commit()


def del_notifications(engine: DB, ntf: Notification):
    with engine.get_session() as session:
        session.delete(ntf)
        session.commit()


def set_next_notification(engine: DB, ntf: Notification, time: 'datetime'):
    with engine.get_session() as session:
        ntf.next_t = time
        session.commit()
