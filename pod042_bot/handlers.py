"""
Обработчики особых событий.
"""
import logging
import math
from io import BytesIO

import numpy as np
import telegram
import vk_api
from pydub import AudioSegment
from telegram import Update, InlineKeyboardButton, ParseMode, InlineKeyboardMarkup, TelegramError
from telegram.ext import CallbackContext

from pod042_bot import models, vk_client

log = logging.getLogger('pod042-bot')


def error(update: Update, context: CallbackContext):
    """Обрабатывает ошибки (но работает ли?...)"""
    error: TelegramError = context.error
    log.error(f'Got error! {error}')
    # noinspection PyBroadException
    try:
        update.message.reply_text(f'Произошла ошибка, пожалуйста, свяжитесь с @saber_nyan :(\n'
                                  f'{error}')
    except Exception:
        log.warning('Failed to notify user!', exc_info=True)


def all_messages(update: Update, context: CallbackContext):
    """Обрабатывает ВСЕ сообщения."""
    if update.channel_post:
        return
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


def inline_button(update: Update, context: CallbackContext):
    """Обрабатывает нажатия кнопок."""
    query = update.callback_query
    chat_id = query.message.chat_id
    msg_id = query.message.message_id
    if query.data == 'vk_config':
        log.debug(f'Starting VK configuration with chat #{chat_id}')
        with models.session_scope() as session:
            chat: models.Chat = session.query(models.Chat).get(chat_id)
            chat.state = models.ChatState.VK_CONFIG
            keyboard = []
            for group in chat.vk_groups:
                keyboard.append([InlineKeyboardButton(group.name, callback_data=f'vkd_{group.url_name}'), ])

        context.bot.edit_message_text('Редактирование групп ВК!\n'
                                      'Нажмите на группу для удаления, отправьте ссылку для добавления, '
                                      '/abort для отмены.', chat_id=chat_id, message_id=msg_id,
                                      reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith('vkd_'):
        url_name = query.data.split('vkd_', 1)[1]
        with models.session_scope() as session:
            chat: models.Chat = session.query(models.Chat).get(chat_id)
            # noinspection PyBroadException
            try:
                chat.vk_groups.remove(session.query(models.VkGroup).get(url_name))
            except Exception:
                log.warning(f'No such VkGroup ({url_name}) in {chat}!', exc_info=True)
            keyboard = []
            for group in chat.vk_groups:
                keyboard.append([InlineKeyboardButton(group.name, callback_data=f'vkd_{group.url_name}'), ])

        context.bot.edit_message_text('Редактирование групп ВК!\n'
                                      'Нажмите на группу для удаления, отправьте ссылку для добавления, '
                                      '/abort для отмены.', chat_id=chat_id, message_id=msg_id,
                                      reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        log.error(f'Unknown query {query.data}!')


def new_vk_group(update: Update, context: CallbackContext):
    """Добавляет группу ВК, если включен соответствующий режим."""
    with models.session_scope() as session:
        chat: models.Chat = session.query(models.Chat).get(update.effective_chat.id)
        if chat.state != models.ChatState.VK_CONFIG:
            return

        invalid_links = []
        valid_groups = []
        for line in update.message.text.splitlines():
            match = vk_client.VK_GROUP_REGEX.match(line)
            if not match:
                invalid_links.append(line)
                continue
            short_name = match.group(1)
            log.debug(f'Got group {short_name}')
            try:
                response = vk_client.vk.groups.getById(group_id=short_name, fields='id',
                                                       version=vk_client.VK_VER)
            except (vk_api.ApiError, vk_api.ApiHttpError) as e:
                log.debug(f'...but test request failed', exc_info=True)
                invalid_links.append(line)
                continue
            raw_group = response[0]
            log.debug(f'Got VK response: {raw_group}')
            group = models.get_or_create(
                session,
                models.VkGroup,
                url_name=raw_group['screen_name'],
                name=raw_group['name']
            )
            valid_groups.append(group)
        chat.vk_groups.extend(valid_groups)

        msg = 'Для остановки нажмите /abort\n'
        if valid_groups:
            msg += '<b>Добавлено:</b>\n'
            for entry in valid_groups:
                msg += str(entry) + '\n'

        if invalid_links:
            msg += '<b>Не добавлено:</b>\n'
            for entry in invalid_links:
                msg += entry + '\n'
    update.message.reply_text(msg, parse_mode=ParseMode.HTML)


def bassboost(update: Update, context: CallbackContext):
    """РАЗБЕЖАВШИСЬ, ДЕЛАЕТ БАССБУСТ"""
    log.debug('Bassboost started!')

    def bass_line_freq(track):
        sample_track = list(track)
        context.bot.edit_message_text('БYСTNНГ: 2/8',
                                      progress_msg.chat_id,
                                      progress_msg.message_id)
        # c-value
        est_mean = np.mean(sample_track)
        context.bot.edit_message_text('БYСTNНГ: 3/8',
                                      progress_msg.chat_id,
                                      progress_msg.message_id)
        # a-values
        est_std = 3 * np.std(sample_track) / (math.sqrt(2))
        context.bot.edit_message_text('БYСTNНГ: 4/8',
                                      progress_msg.chat_id,
                                      progress_msg.message_id)
        bass_factor = int(round((est_std - est_mean) * 0.005))
        context.bot.edit_message_text('БYСTNНГ: 5/8',
                                      progress_msg.chat_id,
                                      progress_msg.message_id)
        return bass_factor

    update.message.reply_text('<b><i><u>РАЗБЕЖАВШИСЬ, ДЕЛАЮ БАССБУСТ</u></i></b>',
                              parse_mode=ParseMode.HTML)
    progress_msg: telegram.Message = update.message.reply_text('БYСTNНГ: 0/8')
    file_info: telegram.File = update.message.audio.get_file()
    log.debug(f'Got file_info: {file_info}')
    byte_array = file_info.download_as_bytearray()
    in_buffer = BytesIO(byte_array)
    out_buffer = BytesIO()
    log.debug('Downloaded, processing...')
    sample = AudioSegment.from_file(in_buffer, format='mp3')
    context.bot.edit_message_text('БYСTNНГ: 1/8',
                                  progress_msg.chat_id,
                                  progress_msg.message_id)

    filtered = sample.low_pass_filter(bass_line_freq(sample.get_array_of_samples()))
    context.bot.edit_message_text('БYСTNНГ: 6/8',
                                  progress_msg.chat_id,
                                  progress_msg.message_id)
    combined = (sample + 5).overlay(filtered + 10)
    context.bot.edit_message_text('БYСTNНГ: 7/8',
                                  progress_msg.chat_id,
                                  progress_msg.message_id)
    combined.export(out_buffer, codec='libmp3lame', format='mp3', bitrate='320')
    context.bot.edit_message_text('БYСTNНГ: 8/8!!',
                                  progress_msg.chat_id,
                                  progress_msg.message_id)
    log.debug('Processed, sending...')
    update.message.reply_audio(out_buffer)
