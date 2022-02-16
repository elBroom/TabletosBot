from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class DB:
    def __init__(self, path):
        self.session = Session(bind=create_engine(path+'?check_same_thread=false'))


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    name = Column(String)
    time = Column(String)
    dosage = Column(String)


def add_notifications(session: Session, nts: Notification):
    nts = Notification(
        chat_id=nts.chat_id,
        name=nts.name,
        time=nts.time,
        dosage=nts.dosage,
    )
    session.add(nts)
    session.commit()
    return nts.id


def get_notifications(session: Session, chat_id=None):
    qs = session.query(Notification)
    if chat_id:
        qs = qs.filter_by(chat_id=chat_id)
    return qs.all()


def get_notification(session: Session, nid: int, chat_id: int):
    return session.query(Notification).filter_by(id=nid, chat_id=chat_id).one()


def del_notifications(session: Session, nts: Notification):
    session.delete(nts)
    session.commit()
