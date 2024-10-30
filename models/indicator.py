import asyncio
import logging
from typing_extensions import Dict, Optional

from sqlalchemy import text

import settings
from models import mongo_client, sql_engine


LOGGER = logging.getLogger(__name__)


class Indicators:
    def __init__(self, server: str) -> None:
        self.db = mongo_client.get_database(settings.MONGODB_NAME)
        self.server = server

    @staticmethod
    def init_indicators() -> None:
        """
        Cria as condições de banco para os indicadores.
        """
        async def migrate():
            db = mongo_client.get_database(settings.MONGODB_NAME)
            quoters = db.get_collection('quoters')
            requesters = db.get_collection('requesters')

            try:
                await quoters.create_index('server', unique=True)
            except Exception as e:
                LOGGER.debug(e)

            try:
                await requesters.create_index('server', unique=True)
            except Exception as e:
                LOGGER.debug(e)

        asyncio.run(migrate())

    async def calculate_quoters(self) -> None:
        """
        Cria o indicador para determinado servidor.
        """
        LOGGER.info('Init indicator quoters process for server %s.', self.server)
        coll = self.db.get_collection(f'quoters')
        _exists = coll.find_one({ 'server': self.server })
        _document = dict()

        async with sql_engine.begin() as session:
            stmt = text(f"""
                select created_by, count(id)
                from quotes
                where server = {self.server}
                group by created_by;
            """)
            cursor = await session.execute(stmt)
            response = cursor.scalars().all()

        for name, total in response:
            _document[name] = total

        if not _exists:
            _document['server'] = self.server
            coll.insert_one(_document)
        else:
            coll.update_one(
                { 'server': self.server },
                _document,
            )

        LOGGER.info('Finish indicator quoters process for server %s.', self.server)

    async def add_request_for(self, username: str) -> None:
        """
        Adiciona no contador de 
        """
        LOGGER.info('Add one more request for quote to %s', username)
        coll = self.db.get_collection('requesters')
        requesters = await coll.find_one({ 'server': self.server })
        _documents = dict(requesters) if requesters else None

        if not _documents:  # Servidor sem indicador.
            coll.insert_one({
                'server': self.server,
                username: 1,
            })
            return

        _documents.pop('server')  # Campo que não sofre update.

        if not _documents.get(username):  # Usuário sem indicador.
            _documents[username] = 1
        else:
            _documents[username] += 1

        await coll.update_one(
            { 'server': self.server },
            _documents,
        )

    async def get_quoters(self) -> Optional[Dict]:
        """
        Captura o indicador de quotadores do server.
        """
        LOGGER.info('Getting quoters for server %s', self.server)
        coll = self.db.get_collection('quoters')
        requesters = await coll.find_one({ 'server': self.server })

        if not requesters:
            return

        _response = dict(requesters)
        _response.pop('server')
        return _response

    async def get_requesters(self) -> Optional[Dict]:
        """
        Captura o indicador de requisitores do server.
        """
        LOGGER.info('Getting requesters for server %s', self.server)
        coll = self.db.get_collection('requesters')
        requesters = await coll.find_one({ 'server': self.server })

        if not requesters:
            return

        _response = dict(requesters)
        _response.pop('server')
        return _response
