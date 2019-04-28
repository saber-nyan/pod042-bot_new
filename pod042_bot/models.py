"""
Модели БД.
"""
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from pod042_bot import config

log = logging.getLogger('pod042-bot')

engine = create_engine(config.DATABASE_URL)
Base = declarative_base()

user_and_chat_association = Table(
    'user_and_chat', Base.metadata,
    Column('chats_chat_id', Integer, ForeignKey('chats.chat_id')),
    Column('users_user_id', Integer, ForeignKey('users.user_id'))
)


class Chat(Base):
    """Личный или групповой чат."""
    __tablename__ = 'chats'

    chat_id = Column(Integer, primary_key=True)
    chat_title = Column(String, nullable=True)

    users = relationship(
        'User',
        secondary=user_and_chat_association,
        back_populates='chats'
    )

    def __repr__(self) -> str:
        return f'<Chat(chat_id={self.chat_id})>'


class User(Base):
    """Пользователь."""
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String)

    chats = relationship(
        'Chat',
        secondary=user_and_chat_association,
        back_populates='users'
    )


def init_db():
    """Создает глобальную сессию."""
    global Session
    Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Удобная обертка для открытия безопасного сессий БД."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        log.warning('Caught exception, trying to rollback DB transaction', exc_info=True)
        session.rollback()
        raise
    finally:
        session.close()
