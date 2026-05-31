import os
from logging import config as logConf


BBC_NEWS_URL = os.environ.get('BBC_NEWS_URL', 'https://www.bbc.com/portuguese/topics/cmdm4ynm24kt')
CNN_NEWS_URL = os.environ.get('CNN_NEWS_URL', 'https://www.cnnbrasil.com.br/internacional/')
TEC_MUNDO_URL = os.environ.get('TEC_MUNDO_URL', 'https://www.tecmundo.com.br/novidades')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
__MARIADB_HOST = os.environ.get('MARIADB_HOST', 'localhost')
__MARIADB_PORT = int(os.environ.get('MARIADB_PORT', '3306'))
__MARIADB_USER = os.environ.get('MARIADB_USER')
__MARIADB_PASSWORD = os.environ.get('MARIADB_PASSWORD')
__MARIADB_DATABASE = os.environ.get('MARIADB_DATABASE', 'lunabot')
REDIS_URI = os.environ.get('REDIS_URI', 'redis://localhost:6379/0')
LOGLEVEL = os.environ.get('LOGLEVEL', 'debug').upper()

MARIADB_URI = f'mysql+asyncmy://{__MARIADB_USER}:{__MARIADB_PASSWORD}@'\
    f'{__MARIADB_HOST}:{__MARIADB_PORT}/{__MARIADB_DATABASE}'

logConf.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] -> %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': LOGLEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'level': LOGLEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
    }
})
