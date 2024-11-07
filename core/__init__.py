import logging
from typing_extensions import Optional, Union, List
from datetime import datetime, timedelta, timezone

from discord import Embed

from models import RedisBase, RedisOrm
from models.quote import Quotes

LOGGER = logging.getLogger(__name__)


def naive_dt_utc_br(dt: datetime) -> str:
    """
    Retorna uma string no formato de data BR.
    """
    return dt.astimezone(timezone(timedelta(hours=-3)))\
        .strftime('%d/%m/%Y %H:%M:%S')


def get_command_message(message: str) -> Optional[str]:
    """
    Retornar a mensagem sem o comando.
    """
    message = message.split(' ')
    _, _message = message[0], message[1:]

    if not _message:
        return

    return ' '.join(_message)


def get_command_args(message: str) -> Union[str, List[str], None]:
    """
    Retornar uma lista com os argumentos do comando.
    """
    message = message.split(' ')
    _, _message = message[0], message[1:]

    if len(message) > 1:
        return _message[0]

    return _message


def prettify_quote(quote: Quotes) -> Embed:
    """
    Embeleza o quote.
    """
    message = str(quote.message)
    ext = message[-5:].split('.')
    ext = ext[1] if len(ext) == 2 else ''
    embed = Embed()

    if  ext in ['png', 'jpg', 'gif', 'mp4']:
        embed.add_field(
            name='ID',
            value=quote.id,
        )
        embed.add_field(
            name='Criado em',
            value=naive_dt_utc_br(quote.created_at),
        )
        embed.add_field(
            name='Criado por',
            value=quote.created_by,
        )
        embed.set_image(url=quote.message)
    else:
        embed.add_field(
            name='ID',
            value=quote.id,
        )
        embed.add_field(
            name='Criado em',
            value=naive_dt_utc_br(quote.created_at),
        )
        embed.add_field(
            name='Criado por',
            value=quote.created_by,
        )
        embed.add_field(
            name='Mensagem',
            value=quote.message,
            inline=False,
        )

    return embed


class Controll(RedisBase):
    """
    Crontrola comportamentos relativos ao gerenciamento de usabilidade do bot.
    """
    def __init__(self, server: str) -> None:
        if not isinstance(server, str):
            server = str(server)

        self.server = server

    async def set_last_quote(self, quoteid: int) -> None:
        """
        Salva o ID do último quote usado.
        """
        try:
            if not isinstance(quoteid, int):
                quoteid = str(quoteid)

            async with RedisOrm() as client:
                await client.set(self.server, quoteid)
        except Exception as e:
            LOGGER.debug(e)
            raise e

        LOGGER.info('Server: %s\nLast quote ID: %s' % (self.server, quoteid))

    async def get_last_quote(self) -> Optional[int]:
        """
        Recupera o ID do últimoquote usado.
        """
        try:
            async with RedisOrm() as client:
                data = await client.get(self.server)

            return int(data) if data else None
        except Exception as e:
            LOGGER.debug(e)
            raise e

    async def set_last_message(self, userid: int, message: str) -> None:
        """
        Salva a última mensagem do usuário para o servidor.
        """
        try:
            key = f'{self.server}:{userid}'

            if not isinstance(message, str):
                message = str(message)

            async with RedisOrm() as client:
                await client.set(key, message)
        except Exception as e:
            LOGGER.debug(e)
            raise e

        LOGGER.info('Server: %s | User: %s Last message: %s' % (self.server, userid, message))

    async def get_last_message(self, userid: int) -> Optional[str]:
        """
        Captura a última mensagem do usuário.
        """
        try:
            key = f'{self.server}:{userid}'

            async with RedisOrm() as client:
                data = await client.get(key)

            return data
        except Exception as e:
            LOGGER.debug(e)
            raise e
