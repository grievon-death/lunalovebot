from pymongo import AsyncMongoClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

import settings


class BaseTable(AsyncAttrs, DeclarativeBase):
    """
    Modelo mestre.
    """
    pass


sql_engine = create_async_engine(settings.MARIADB_URI)
mongo_client = AsyncMongoClient(settings.MONGODB_URL)
