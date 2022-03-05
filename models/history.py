import datetime
import pytz

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from db import Base, DB


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


def add_history(engine: DB, ntf: 'Notification', timezone: str, time: str = ''):
    if not time:
        created_at = datetime.datetime.now(pytz.timezone(timezone))
    else:
        created_at = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M').replace(tzinfo=pytz.timezone(timezone))

    with engine.get_session() as session:
        session.add(History(
            created_at=created_at,
            chat_id=ntf.chat_id,
            name=ntf.name,
            dosage=ntf.dosage,
        ))
        session.commit()
    return ntf.id


def get_history(engine: DB, chat_id=None):
    with engine.get_session() as session:
        qs = session.query(History).order_by(History.created_at)
        if chat_id:
            qs = qs.filter_by(chat_id=chat_id)
        return qs.all()


def get_history_row(engine: DB, hid: int, chat_id: int):
    with engine.get_session() as session:
        return session.query(History).filter_by(id=hid, chat_id=chat_id).one()


def del_history_row(engine: DB, log: History):
    with engine.get_session() as session:
        session.delete(log)
        session.commit()
