"""
Создает конфигурацию из переменных окружения.
"""
import os
import sys

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    """Токен бота, получать у @BotFather."""
    PRODUCTION = bool(os.getenv('PRODUCTION', False))
    """True, если бот размещен на Heroku."""
    if PRODUCTION:
        HEROKU_APP_NAME = os.environ['HEROKU_APP_NAME']
        """Имя приложения Heroku."""
        PORT = os.environ['PORT']
        """Какой порт слушать боту (выставляет сам Heroku)."""
except KeyError as e:
    sys.stderr.write('Приложение не сконфигурировано, проверьте необходимые переменные окружения в config.py!\n'
                     f'Не хватает переменной "{e.args[0]}"\n')
    sys.exit(-1)

LOG_FORMAT = os.getenv('LOG_FORMAT', 'P%(process)d T%(thread)d %(asctime)s <%(filename)s:'
                                     '%(lineno)d, %(funcName)s()> [%(levelname)s] %(name)s: %(message)s')
"""
Формат лога, см.
https://docs.python.org/3/library/logging.html#logrecord-attributes
"""

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
"""Подробность лога."""

PROXY_HOST = os.getenv('PROXY_HOST')
"""Имя хоста SOCKS5 прокси-сервера."""
PROXY_PORT = os.getenv('PROXY_PORT')
"""Порт прокси-сервера."""
PROXY_USER = os.getenv('PROXY_USER')
"""Пользователь прокси-сервера (опционально)."""
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')
"""Пароль прокси-сервера (опционально)."""
