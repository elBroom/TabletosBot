import datetime
import pytz

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from db import Base


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())

    chat_id = Column(Integer)
    name = Column(String)
    dosage = Column(String)

    @property
    def datetime(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M')


def add_history(session: Session, ntf: 'Notification', timezone: str, time: str = ''):
    if not time:
        created_at = datetime.datetime.now(pytz.timezone(timezone))
    else:
        created_at = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M').replace(tzinfo=pytz.timezone(timezone))
    session.add(History(
        created_at=created_at,
        chat_id=ntf.chat_id,
        name=ntf.name,
        dosage=ntf.dosage,
    ))
    session.commit()
    return ntf.id


def get_history(session: Session, chat_id: int):
    qs = session.query(History).filter_by(chat_id=chat_id).order_by(History.created_at)
    return qs.all()


def get_history_row(session: Session, hid: int, chat_id: int):
    return session.query(History).filter_by(id=hid, chat_id=chat_id).one()


def del_history_row(session: Session, log: History):
    session.delete(log)
    session.commit()
