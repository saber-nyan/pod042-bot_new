"""
Основной модуль.
"""
import logging.config
import socket

from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler

from pod042_bot import config, commands, models, handlers, vk_client

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

    if not config.PRODUCTION:
        old_getaddrinfo = socket.getaddrinfo

        def new_getaddrinfo(*args, **kwargs):
            """Патч для отключения IPv6."""
            responses = old_getaddrinfo(*args, **kwargs)
            return [response
                    for response in responses
                    if response[0] == socket.AF_INET]

        socket.getaddrinfo = new_getaddrinfo

    models.init_db()

    vk_client.init_vk()

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
        workers=config.THREADS_NUM,
        request_kwargs=request_kwargs
    )

    d = updater.dispatcher
    d.add_handler(MessageHandler(Filters.all, handlers.all_messages), group=-3)

    d.add_handler(CommandHandler('abort', commands.abort), group=-2)

    d.add_handler(MessageHandler(Filters.text, handlers.new_vk_group), group=-1)

    d.add_handler(CommandHandler('start', commands.start))
    d.add_handler(CommandHandler('vk_pic', commands.vk_pic))
    d.add_handler(CommandHandler('codfish', commands.codfish, pass_args=True))
    d.add_handler(CommandHandler('pat', commands.pat, pass_args=True))
    d.add_handler(CommandHandler('anek', commands.anek))
    d.add_handler(CommandHandler('quote', commands.quote))
    d.add_handler(CommandHandler('config', commands.config))
    d.add_handler(MessageHandler(Filters.regex(r'@(all|everyone|room)'), commands.everyone))
    d.add_handler(MessageHandler(Filters.audio, handlers.bassboost))

    d.add_handler(CallbackQueryHandler(handlers.inline_button))

    d.add_error_handler(handlers.error)

    log.info('Init complete, starting polling...')
    run_bot(updater)


if __name__ == '__main__':
    main()
