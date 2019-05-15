"""
Всякие разные утилиты для жизни хорошей.
"""
from typing import List

from pod042_bot import models


def get_names(args: List[str], bot_username: str, session: models.orm.Session, chat: models.Chat) \
        -> List[str]:
    """
    Забирает список юзернеймов из сообщения и возвращает список имен.

    :param List[str] args: юзернеймы
    :param str bot_username: юзернейм бота
    :param models.orm.Session session: сессия БД
    :param models.Chat chat: текущий чат
    :rtype: List[str]
    """
    args = list(map(lambda e: e.replace('@', ''), args))
    known_users: List[models.User] = session.query(models.User) \
        .join(models.User.chats) \
        .filter(models.User.username.in_(args),
                models.Chat.chat_id == chat.chat_id)
    result = list(map(lambda e: e.first_name, known_users))
    if bot_username in args:
        result.append('себя')
    return result
