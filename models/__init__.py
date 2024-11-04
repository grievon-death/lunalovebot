import redis.asyncio as redis
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

import settings


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


sql_engine = create_engine(settings.MARIADB_URI)
