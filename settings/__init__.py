import os
from logging import config as logConf


BBC_NEWS_URL = 'https://www.bbc.com/portuguese/topics/cmdm4ynm24kt'
BOT_TOKEN = os.environ.get('BOT_TOKEN')
MARIADB_URI = os.environ.get('MARIADB_URI', 'mysql://root:root@localhost:3306/lunabot')
REDIS_URI = os.environ.get('REDIS_URI', 'redis://localhost:6379/0')
LOGLEVEL = os.environ.get('LOGLEVEL', 'debug').upper()
LOGFILE = os.environ.get('LOGFILE', '/tmp/lunabotgood.log')

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
        'logfile': {
            'level': LOGLEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGFILE,
            'maxBytes': 200000000,  # 200MB
            'backupCount': 5,
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'level': LOGLEVEL,
            'handlers': ['console', 'logfile'],
            'propagate': False,
        },
    }
})
