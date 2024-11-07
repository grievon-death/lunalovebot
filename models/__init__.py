import logging
from typing_extensions import Dict, List, Optional

import redis.asyncio as redis
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

import settings


LOGGER = logging.getLogger(__name__)


class BaseTable(DeclarativeBase):
    """
    Modelo mestre.
    """
    pass


class RedisBase:
    async def _decode_dict(self, data: Dict) -> Optional[Dict]:
        """
        No retorno todos os campos vêm como bytearray, então tem que fazer esse processo aqui.
        """
        try:
            return { k.decode(): int(v.decode()) for k, v in data.items()}
        except Exception as e:
            LOGGER.debug(e)
            raise e


class RedisOrm:
    def __init__(self) -> None:
        self.pool = redis\
            .BlockingConnectionPool(decode_responses=True)\
            .from_url(settings.REDIS_URI)

    async def __aenter__(self) -> redis.Redis:
        self.client = redis.Redis(connection_pool=self.pool)
        return self.client

    async def __aexit__(self, excp_a, excp_b, excp_c) -> None:
        await self.pool.disconnect()
        await self.client.close()


sql_engine = create_engine(
    settings.MARIADB_URI,
    echo_pool=True,
    pool_pre_ping=True,
    pool_recycle=600,
)
