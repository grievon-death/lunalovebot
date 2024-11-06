import logging
from typing_extensions import Dict, Optional

from models import RedisBase, RedisOrm


LOGGER = logging.getLogger(__name__)


class Indicators(RedisBase):
    def __init__(self, server: str) -> None:
        self.qkey = f'q:{server}'
        self.rqkey = f'rq:{server}'

    async def q_usage(self, username: str) -> None:
        """
        Adiciona no contador do comando quotes.
        """
        try:
            LOGGER.info('Add one more quote to %s', username)
            _indicator = await self.q_get()

            async with RedisOrm() as client:
                if not _indicator:
                    await client.hmset(
                        self.qkey,
                        {
                            username: 1
                        }
                    )
                elif not _indicator.get(username):
                    _indicator[username] = 1
                else:
                    _indicator[username] += 1

                await client.hmset(
                    self.qkey,
                    _indicator,
                )

        except Exception as e:
            LOGGER.debug(e)
            raise e

    async def rq_usage(self, username: str) -> None:
        """
        Adiciona no contador do comando randomquote.
        """
        try:
            LOGGER.info('Add one more random quote to %s', username)
            _indicator = await self.rq_get()

            async with RedisOrm() as client:
                if not _indicator:
                    await client.hmset(
                        self.rqkey,
                        {
                            username: 1
                        }
                    )
                elif not _indicator.get(username):
                    _indicator[username] = 1
                else:
                    _indicator[username] += 1

                await client.hmset(
                    self.rqkey,
                    _indicator,
                )

        except Exception as e:
            LOGGER.debug(e)
            raise e

    async def q_get(self) -> Optional[Dict]:
        """
        Captura o indicador de quotadores do server.
        """
        try:
            LOGGER.info('Getting quoters for server %s', self.qkey)
            
            async with RedisOrm() as client:
                content = await client.hgetall(self.qkey)
                content = await self._decode_dict(content)

            return content
        except Exception as e:
            LOGGER.debug(e)
            raise e

    async def rq_get(self) -> Optional[Dict]:
        """
        Captura o indicador de requisitores do server.
        """
        try:
            LOGGER.info('Getting requesters for server %s', self.rqkey)

            async with RedisOrm() as client:
                content = await client.hgetall(self.rqkey)
                content = await self._decode_dict(content)

            return content
        except Exception as e:
            LOGGER.debug(e)
            raise e
