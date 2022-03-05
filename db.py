from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class NoResultFoundErr(NoResultFound):
    pass


class DB:
    def __init__(self, path):
        self.session = Session(bind=create_engine(f'{path}?check_same_thread=false', pool_pre_ping=True))
