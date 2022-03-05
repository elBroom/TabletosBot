from sqlalchemy import Column, Boolean, Integer, String
from sqlalchemy.orm import Session

from db import Base, DB, NoResultFound


class Setting(Base):
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    timezone = Column(String, default='Europe/Moscow')
    interval_alert = Column(Integer, default=20)
    take_photo = Column(Boolean, default=True)
    urgency_enabled = Column(Boolean, default=True)


def add_setting(engine: DB, obj: Setting):
    with engine.get_session() as session:
        session.add(obj)
        session.commit()
    return obj.id


def get_setting(engine: DB, chat_id: int) -> Setting:
    with engine.get_session() as session:
        try:
            return session.query(Setting).filter_by(chat_id=chat_id).one()
        except NoResultFound:
            return Setting(chat_id=chat_id)
