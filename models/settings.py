from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from db import Base


class Settings(Base):
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    timezone = Column(String)
    name = Column(String)


def add_setting(session: Session, obj: Settings):
    session.add(obj)
    session.commit()
    return obj.id


def get_setting(session: Session, chat_id: int):
    return session.query(Settings).filter_by(chat_id=chat_id).one()
