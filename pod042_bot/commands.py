"""
Функции команд бота.
"""
import logging

from sqlalchemy.orm import selectinload
from telegram import Bot, Update

from pod042_bot import models

log = logging.getLogger('pod042-bot')


def all_messages(bot: Bot, update: Update):
    """Обрабатывает ВСЕ сообщения."""
    if not update.channel_post:
        cur_user = update.effective_user
        cur_chat = update.effective_chat
        log.debug(f'Got message from #{cur_user.id}')
        with models.session_scope() as session:
            user = models.get_or_create(
                session,
                models.User,
                user_id=cur_user.id,
                username=cur_user.username,
                first_name=cur_user.first_name,
                last_name=cur_user.last_name
            )
            chat = models.get_or_create(
                session,
                models.Chat,
                chat_id=cur_chat.id,
                chat_title=cur_chat.title
            )
            if chat not in user.chats:
                user.chats.append(chat)


def start(bot: Bot, update: Update):
    """Простое приветствие!"""
    log.info(f'User #{update.effective_user.id} started bot')
    update.message.reply_text('Started, thanks!')


def everyone(bot: Bot, update: Update):
    """Упоминает всех в чате."""
    if update.channel_post:
        return
    with models.session_scope() as session:
        users = session.query(models.Chat) \
            .options(selectinload(models.Chat.users)) \
            .get(update.effective_chat.id) \
            .users
        user: models.User
        usernames = ''
        for user in users:
            if user.username:
                usernames += f'@{user.username} '
    if usernames:
        update.effective_chat.send_message(usernames)
    else:
        update.effective_chat.send_message('Никого не знаю!')
