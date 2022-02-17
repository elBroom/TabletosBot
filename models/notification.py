from sqlalchemy import Boolean, Column, Integer, String
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


def add_notification(session: Session, ntf: Notification):
    session.add(ntf)
    session.commit()
    return ntf.id


def get_notifications(session: Session, chat_id=None):
    qs = session.query(Notification)
    if chat_id:
        qs = qs.filter_by(chat_id=chat_id)
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
