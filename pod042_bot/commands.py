"""
Функции команд бота.
"""
import logging
import random
import re
from typing import List, Dict

import pkg_resources
import requests
from sqlalchemy.orm import selectinload
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ChatAction
from telegram.ext import CallbackContext

from pod042_bot import models, vk_client, utils

HTML_ANEK_REGEX = re.compile(r'<meta name="description" content="(.*?)">', re.DOTALL)

log = logging.getLogger('pod042-bot')


def abort(update: Update, context: CallbackContext):
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


def start(update: Update, context: CallbackContext):
    """Простое приветствие!"""
    log.info(f'User #{update.effective_user.id} started bot')
    update.message.reply_text('Ура, я запущен!')


def everyone(update: Update, context: CallbackContext):
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


def config(update: Update, context: CallbackContext):
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


def vk_pic(update: Update, context: CallbackContext):
    """Возвращает случайно выбранное медиа из настроенных для чата групп ВКонтакте."""
    with models.session_scope() as session:
        chat: models.Chat = session.query(models.Chat).get(update.effective_chat.id)
        groups = chat.vk_groups
        if not groups:
            update.message.reply_text('Сначала настройте группы с помощью /config!')
            return
        context.bot.send_chat_action(update.effective_chat.id, ChatAction.UPLOAD_PHOTO)
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
            if post.get('marked_as_ads', False):
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
        # update.message.reply_text(f'{media_url}\n'
        #                           f'Из https://vk.com/{chosen_group.url_name}')
        update.message.reply_photo(photo=media_url, caption=f'Из https://vk.com/{chosen_group.url_name}')


def codfish(update: Update, context: CallbackContext):
    """Бьет треской по лицу выбранных пользователей. С видео!"""
    args = context.args
    bot = context.bot
    if not args:
        update.message.reply_text('Неверный формат команды. Пиши `/codfish @user_name1 @user_name2 ...`!',
                                  parse_mode=ParseMode.MARKDOWN)
        return
    bot.send_chat_action(update.effective_chat.id, ChatAction.RECORD_VIDEO)
    with models.session_scope() as session:
        chat: models.Chat = session.query(models.Chat).get(update.effective_chat.id)
        result = utils.get_names(args, session, chat)
        with pkg_resources.resource_stream('pod042_bot.resources.videos', 'codfish.mp4') as f:
            if any(x in args for x in ('@all', '@everyone', '@room')):
                bot.send_video(update.effective_chat.id, f,
                               caption='Отпиздил треской всю комнату, да и себя ебанул, для профилактики.')
            elif len(args) == 1 and (args[0][1:] == bot.username or args[0][1:] == bot.first_name):
                bot.send_video(update.effective_chat.id, f,
                               caption='Хорошенько пизданул себя треской.')
            else:
                if not result:
                    update.message.reply_text('Не смог никого вспомнить...')
                    return
                if bot.username in args or bot.first_name in args:
                    bot.send_video(
                        update.effective_chat.id, f,
                        caption=f'Со всего размаху пизданул треской '
                                f'{", ".join(result)}, да и для себя трески не пожалел.'
                    )
                else:
                    bot.send_video(update.effective_chat.id, f,
                                   caption=f'Со всего размаху пизданул треской {", ".join(result)}.')


def pat(update: Update, context: CallbackContext):
    """Гладит указанных пользователей. Да, тоже с видео!"""
    args = context.args
    bot = context.bot
    if not args:
        update.message.reply_text('Неверный формат команды. Пиши `/pat @user_name1 @user_name2 ...`!',
                                  parse_mode=ParseMode.MARKDOWN)
        return
    bot.send_chat_action(update.effective_chat.id, ChatAction.RECORD_VIDEO)
    with models.session_scope() as session:
        chat: models.Chat = session.query(models.Chat).get(update.effective_chat.id)
        result = utils.get_names(args, session, chat)
        with pkg_resources.resource_stream('pod042_bot.resources.videos', 'pat.mp4') as f:
            if any(x in args for x in ('@all', '@everyone', '@room')):
                bot.send_video(update.effective_chat.id, f,
                               caption='Ментально погладил всех в комнате!')
            elif len(args) == 1 and (args[0][1:] == bot.username or args[0][1:] == bot.first_name):
                bot.send_video(update.effective_chat.id, f,
                               caption='Сам себя не погладишь – никто не погладит...')
            else:
                if not result:
                    update.message.reply_text('Не смог никого вспомнить...')
                    return
                if bot.username in args or bot.first_name in args:
                    bot.send_video(update.effective_chat.id, f,
                                   caption=f'Ментально погладил {", ".join(result)}, да и себя не обидел!')
                else:
                    bot.send_video(update.effective_chat.id, f,
                                   caption=f'Ментально погладил {", ".join(result)}!')


def anek(update: Update, context: CallbackContext):
    """Присылает рандомный анекдот с baneks.ru."""
    response = requests.get(f'https://baneks.ru/{random.randrange(1, 1142)}')
    response.encoding = 'utf-8'
    matches = HTML_ANEK_REGEX.search(response.text)
    result = matches.group(1) if matches else 'Ошибка...'
    update.message.reply_text(f'<code>{result}</code>', parse_mode=ParseMode.HTML)


def quote(update: Update, context: CallbackContext):
    """Присылает рандомную цитату с tproger.com."""
    result = requests.get('https://tproger.ru/wp-content/plugins/citation-widget/get-quote.php').text
    update.message.reply_text(f'<code>{result}</code>', parse_mode=ParseMode.HTML)
