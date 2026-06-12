import json
import logging
from typing import List, Self

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

import settings


LOGGER = logging.getLogger(__name__)


class BaseTable(DeclarativeBase):
    """
    Modelo mestre.
    """
    pass


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


class Cache:
    """
    Cache da lista de últimos ID's dos quotes retornados durante o uso do BOT.
    """
    def __init__(self, server: str) -> Self:
        self.key = f'c:{server}'

    async def insert(self, data: List[int]) -> None:
        """
        Adiciona a lista no cache.
        """
        try:
            async with RedisOrm() as cache:
                await cache.set(self.key, json.dumps(data))
        except Exception as e:
            LOGGER.error(f'Cannot insert list on Redis.\nCause: {e}')

    async def get(self) -> List[int]:
        """
        Captura a lista do cache.
        """
        try:
            async with RedisOrm() as cache:
                data = await cache.get(self.key)

            return json.loads(data) if data else []
        except Exception as e:
            LOGGER.error(f'Cannot get list from Redis.\nCause: {e}')
            return []


sql_engine = create_async_engine(
    settings.MARIADB_URI,
    echo_pool=True,
    pool_pre_ping=True,
    pool_recycle=600,
)
