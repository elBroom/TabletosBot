from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class NoResultFoundErr(NoResultFound):
    pass


class DB:
    def __init__(self, path):
        self.engine = create_engine(f'{path}?check_same_thread=false', pool_pre_ping=True)

    def get_session(self):
        return Session(bind=self.engine)


def transaction_handler(func):
    def wrapper(update: 'Update', context: 'CallbackContext'):
        with context.bot_data['db'].get_session() as db_session:
            if 'db_session' in context.chat_data:
                context.bot.logger.info('Double db_session')

            context.chat_data['db_session'] = db_session
            res = func(update, context)
            del context.chat_data['db_session']
            return res
    return wrapper
