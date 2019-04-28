"""
Функции команд бота.
"""
import logging

from telegram import Bot, Update

log = logging.getLogger('pod042-bot')


def start(bot: Bot, update: Update):
    """Простое приветствие!"""
    log.info(f'User #{update.effective_user["id"]} started bot')
    update.message.reply_text('Started, thanks!')
