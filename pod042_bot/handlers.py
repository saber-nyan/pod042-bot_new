"""
Обработчики особых событий.
"""
import logging

import vk_api
from telegram import Bot, Update, InlineKeyboardButton, ParseMode, InlineKeyboardMarkup, TelegramError

from pod042_bot import models, vk_client

log = logging.getLogger('pod042-bot')


def error(bot: Bot, update: Update, tg_error: TelegramError):
    """Обрабатывает ошибки (но работает ли?...)"""
    log.error(f'Got error! {tg_error.message}')
    # noinspection PyBroadException
    try:
        update.message.reply_text(f'Произошла ошибка, пожалуйста, свяжитесь с @saber_nyan :(\n'
                                  f'{tg_error.message}')
    except Exception:
        pass


def all_messages(bot: Bot, update: Update):
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


def inline_button(bot: Bot, update: Update):
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

        bot.edit_message_text('Редактирование групп ВК!\n'
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

        bot.edit_message_text('Редактирование групп ВК!\n'
                              'Нажмите на группу для удаления, отправьте ссылку для добавления, '
                              '/abort для отмены.', chat_id=chat_id, message_id=msg_id,
                              reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        log.error(f'Unknown query {query.data}!')


def new_vk_group(bot: Bot, update: Update):
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


def bassboost(bot: Bot, update: Update):
    """РАЗБЕЖАВШИСЬ, ДЕЛАЕТ БАССБУСТ"""
    log.debug('Bassboost started!')

    # def bass_line_freq(track):
    #     sample_track = list(track)
    #     log.debug(2)
    #     # c-value
    #     est_mean = np.mean(sample_track)
    #     log.debug(3)
    #     # a-values
    #     est_std = 3 * np.std(sample_track) / (math.sqrt(2))
    #     log.debug(4)
    #     bass_factor = int(round((est_std - est_mean) * 0.005))
    #     log.debug(5)
    #     return bass_factor
    #
    # update.message.reply_text('БYСTNНГ')
    # file_info: telegram.File = update.message.audio.get_file()
    # log.debug(f'Got file_info: {file_info}')
    # byte_array = file_info.download_as_bytearray()
    # in_buffer = BytesIO(byte_array)
    # out_buffer = BytesIO()
    # log.debug('Downloaded, processing...')
    # sample = AudioSegment.from_file(in_buffer, format='mp3')
    # log.debug(1)
    # filtered = sample.low_pass_filter(bass_line_freq(sample.get_array_of_samples()))
    # log.debug(6)
    # combined = (sample + 5).overlay(filtered + 10)
    # log.debug(7)
    # combined.export(out_buffer, codec='libmp3lame', format='mp3', bitrate='320')
    # log.debug(8)
    # log.debug('Processed, sending...')
    # update.message.reply_audio(out_buffer)
