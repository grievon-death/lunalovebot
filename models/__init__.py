from pymongo import AsyncMongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

import settings


class BaseTable(DeclarativeBase):
    """
    Modelo mestre.
    """
    pass


sql_engine = create_engine(settings.MARIADB_URI)
mongo_client = AsyncMongoClient(settings.MONGODB_URL)
