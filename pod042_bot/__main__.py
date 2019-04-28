"""
Основной модуль.
"""
import logging.config

from telegram.ext import Updater, CommandHandler

from pod042_bot import config, commands

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': config.LOG_FORMAT
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'pod042-bot': {
            'handlers': ['default'],
            'level': config.LOG_LEVEL,
            'propagate': False
        },
    }
})
log = logging.getLogger('pod042-bot')

if config.PRODUCTION:
    def run_bot(updater: Updater):
        """Запускает бота в Webhook-режиме, подходящем для Heroku."""
        updater.start_webhook(
            listen='0.0.0.0',
            port=config.PORT,
            url_path=config.BOT_TOKEN
        )
        updater.bot.set_webhook(f'https://{config.HEROKU_APP_NAME}.herokuapp.com/{config.BOT_TOKEN}')
else:
    def run_bot(updater: Updater):
        """Запускает бота в Long Polling-режиме, удобном при разработке."""
        updater.start_polling()


def main():
    """Инициализирует бота."""
    log.info('Initializing bot...')

    request_kwargs = None
    if config.PROXY_HOST:
        # Shitty RKN...
        request_kwargs = {
            'proxy_url': f'socks5://{config.PROXY_HOST}:{config.PROXY_PORT}',
        }
        if config.PROXY_USER:
            request_kwargs['urllib3_proxy_kwargs'] = {
                'username': config.PROXY_USER,
                'password': config.PROXY_PASSWORD,
            }

    updater = Updater(
        token=config.BOT_TOKEN,
        workers=8,
        request_kwargs=request_kwargs
    )

    updater.dispatcher.add_handler(CommandHandler("start", commands.start))

    log.info('Init complete, starting polling...')
    run_bot(updater)


if __name__ == '__main__':
    main()
