from sqlalchemy import Column, Boolean, Integer, String

from db import Base, NoResultFound


class Setting(Base):
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    timezone = Column(String, default='Europe/Moscow')
    interval_alert = Column(Integer, default=20)
    take_photo = Column(Boolean, default=True)
    urgency_enabled = Column(Boolean, default=True)


def add_setting(session: Session, obj: Setting):
    session.add(obj)
    session.commit()
    return obj.id


def get_setting(session: Session, chat_id: int) -> Setting:
    try:
        return session.query(Setting).filter_by(chat_id=chat_id).one()
    except NoResultFound:
        return Setting(chat_id=chat_id)
