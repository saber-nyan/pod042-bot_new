"""
Функции команд бота.
"""
import logging

from sqlalchemy.orm import selectinload
from telegram import Bot, Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

from pod042_bot import models

log = logging.getLogger('pod042-bot')


def abort(bot: Bot, update: Update):
    """Сбрасывает текущее состояние чата."""
    if update.channel_post:
        return
    with models.session_scope() as session:
        chat: models.Chat = session.query(models.Chat).get(update.effective_chat.id)
        if chat.state == models.ChatState.NONE:
            update.message.reply_text('Я ничем не занят!')
        else:
            chat.state = models.ChatState.NONE
            update.message.reply_text('Отменено.')


def start(bot: Bot, update: Update):
    """Простое приветствие!"""
    log.info(f'User #{update.effective_user.id} started bot')
    update.message.reply_text('Ура, я запущен!')


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


def config(bot: Bot, update: Update):
    """Входит в режим конфигурации."""
    with models.session_scope() as session:
        chat: models.Chat = session.query(models.Chat).get(update.effective_chat.id)
        chat.state = models.ChatState.CONFIG

        vk_groups = ''
        for group in chat.vk_groups:
            vk_groups += f'{group.url_name} ({group.url_name})\n'
        if not vk_groups:
            vk_groups = 'Пусто!'

        msg = (f'Вошел в режим конфигурации.\n\n'
               f'Текущие группы ВК: ```\n{vk_groups}```')
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN,
                              reply_markup=InlineKeyboardMarkup(
                                  [
                                      [InlineKeyboardButton('Изменить группы ВК', callback_data='vk_config'), ],
                                  ]
                              ))
