from argparse import ArgumentParser
from threading import Thread

import settings
from core import daemons, bot
from models import quote


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
            quote.Quotes.migrate()
        case 'bot':
            threads = [
                Thread(
                    target=daemons.indicator
                ),
                Thread(
                    target=bot.client.run,
                    args=(settings.BOT_TOKEN, )
                )
            ]

            for thread in threads:
                thread.start()
            
            for thread in threads:
                thread.join()

        case _:
            pass
