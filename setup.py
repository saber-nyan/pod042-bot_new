"""
Некоторое установочное дерьмо.
"""
import setuptools

with open('README.md', 'rt', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='pod042-bot',
    version='0.0.3',
    author='saber-nyan',
    author_email='saber-nyan@ya.ru',
    license='WTFPL',
    description='Yet another use{less,ful} Telegram bot',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/saber-nyan/pod042-bot-new',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'License :: Public Domain',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications :: Chat',
        'Topic :: Games/Entertainment',
        'Topic :: Internet',
        'Typing :: Typed',
    ],
    install_requires=[
        'python-telegram-bot==12.6.1',
        'python-telegram-bot[socks]==12.6.1',
        'SQLAlchemy==1.3.16',
        'alembic==1.4.2',
        'psycopg2-binary==2.8.5',
        'vk-api==11.8.0',
    ],
)
