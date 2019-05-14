"""Функции для работы с ВКонтакте."""
import json
import logging
import re
from typing import List

from jconfig.base import BaseConfig
from vk_api import VkApi, VkTools

from pod042_bot import config, models

VK_VER = 5.95
VK_GROUP_REGEX = re.compile(r".*vk\.com/(.+?)(\?.+)?$", re.MULTILINE)

log = logging.getLogger('pod042-bot')


class DbConfig(BaseConfig):
    """Костыль для предотвращения переавторизации ВК."""

    def __init__(self, section, filename='.jconfig'):
        self._filename = filename
        super(DbConfig, self).__init__(section, filename=filename)

    def load(self, filename, **kwargs):
        """Загружает настройки из БД."""
        # noinspection PyBroadException
        try:
            with models.session_scope() as session:
                vk_cred: models.VkCred = session.query(models.VkCred).get(filename)
                settings = json.loads(vk_cred.json)
        except Exception:
            log.warning('Failed to load VK settings!', exc_info=True)
            settings = {}
        settings.setdefault(self.section_name, {})
        return settings

    def save(self):
        """Сохраняет настройки в БД."""
        with models.session_scope() as session:
            session.merge(models.VkCred(
                filename=self._filename,
                json=json.dumps(self._settings, sort_keys=True)
            ))

    __slots__ = ('_filename',)


def init_vk():
    """Подготавливает модуль для работы."""
    log.info('VK init...')
    vk_session = VkApi(config.VK_LOGIN, config.VK_PASSWORD,
                       api_version=str(VK_VER), config=DbConfig)
    log.info('...auth...')
    vk_session.auth(token_only=True)
    log.info('...success!')

    global vk
    vk = vk_session.get_api()

    global vk_tools
    vk_tools = VkTools(vk_session)


def get_random_media(groups: List[models.VkGroup]):
    """Случайно выбирает и получает прямую ссылку на медиа из одной из групп."""
    # TODO
    return 'https://www.google.ru/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png'
