"""
Функции команд бота.
"""
import logging
import random
from typing import List, Dict

import pkg_resources
from sqlalchemy.orm import selectinload
from telegram import Bot, Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ChatAction

from pod042_bot import models, vk_client, utils

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

        msg = (f'Вошел в режим конфигурации.\n'
               f'/abort для отмены.\n\n'
               f'Текущие группы ВК: ```\n{vk_groups}```')
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN,
                              reply_markup=InlineKeyboardMarkup(
                                  [
                                      [InlineKeyboardButton('Изменить группы ВК', callback_data='vk_config'), ],
                                  ]
                              ))


def vk_pic(bot: Bot, update: Update):
    """Возвращает случайно выбранное медиа из настроенных для чата групп ВКонтакте."""
    with models.session_scope() as session:
        chat: models.Chat = session.query(models.Chat).get(update.effective_chat.id)
        groups = chat.vk_groups
        if not groups:
            update.message.reply_text('Сначала настройте группы с помощью /config!')
            return
        bot.send_chat_action(update.effective_chat.id, ChatAction.UPLOAD_PHOTO)
        chosen_group: models.VkGroup = random.choice(groups)
        log.debug(f'Selected {chosen_group}')
        response: List[Dict] = vk_client.vk_tools.get_all('wall.get', max_count=10, values={
            'domain': chosen_group.url_name,
            'fields': 'attachments',
            'version': vk_client.VK_VER,
        }, limit=250)['items']
        media_url = ''
        while not media_url:
            post = random.choice(response)
            if post['marked_as_ads']:
                log.debug('Skipping ad')
                continue
            if 'attachments' not in post:
                log.debug('Skipping post w/o attachs')
                continue
            for attach in post['attachments']:
                if 'doc' in attach and attach['doc']['ext'] == 'gif':
                    log.debug('Found gif!')
                    media_url = attach['doc']['url']
                    break
                elif 'photo' in attach:
                    log.debug('Found picture!')
                    sizes_list: List[Dict] = attach['photo']['sizes']
                    avail_codes = map(lambda e: e['type'], sizes_list)
                    if 'w' in avail_codes:
                        code = 'w'
                    elif 'z' in avail_codes:
                        code = 'z'
                    elif 'y' in avail_codes:
                        code = 'y'
                    else:
                        continue
                    element = next(i for i in sizes_list if i['type'] == code)
                    if not element:
                        continue
                    media_url = element['url']
        update.message.reply_text(f'{media_url}\n'
                                  f'Из https://vk.com/{chosen_group.url_name}')


def codfish(bot: Bot, update: Update, args: List[str]):
    """Бьет треской по лицу выбранных пользователей. С видео!"""
    if not args:
        update.message.reply_text('Неверный формат команды. Пиши `/codfish @user_name`!',
                                  parse_mode=ParseMode.MARKDOWN)
        return
    bot.send_chat_action(update.effective_chat.id, ChatAction.RECORD_VIDEO)
    with models.session_scope() as session:
        chat: models.Chat = session.query(models.Chat).get(update.effective_chat.id)
        result = utils.get_names(args, bot.username, session, chat)
        if not result:
            update.message.reply_text('Не смог никого вспомнить...')
            return
        with pkg_resources.resource_stream('pod042_bot.resources.videos', 'codfish.mp4') as f:
            bot.send_video(update.effective_chat.id, f,
                           caption=f'Со всего размаху пизданул {", ".join(result)} треской.')
