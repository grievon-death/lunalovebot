import os
from logging import config as logConf


BOT_TOKEN = os.environ.get('BOT_TOKEN')
MARIADB_URI = os.environ.get('MARIADB_URI', 'mysql://root:root@localhost:3306/lunabot')
MONGODB_URL = os.environ.get('MONGODB_URL', 'mongodb://localhost:27017')
MONGODB_NAME = os.environ.get('MONGODB_NAME', 'lunabot')
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
