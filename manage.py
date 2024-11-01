import logging
from argparse import ArgumentParser
from threading import Thread

import settings
from core import daemons, bot
from models import quote
from models import indicator


LOGGER = logging.getLogger(__name__)

parser = ArgumentParser(description='Luna Lovebot')
parser.add_argument(
    'command',
    type=str,
    action='store',
    help='Command to execute. [ migrate | bot ]',
)


if __name__ == '__main__':
    args = parser.parse_args()

    match args.command:
        case 'migrate':
            try:
                quote.Quotes.migrate()
                indicator.Indicators.init_indicators()
            except Exception as e:
                LOGGER.error(e)
        case 'bot':
            bot.client.run(settings.BOT_TOKEN)
        case _:
            pass
