import asyncio
import logging
from typing_extensions import Dict, Optional

import settings
from models import mongo_client, QUOTTERS_COLLECTION, REGISTERS_COLLECTION


LOGGER = logging.getLogger(__name__)


class Indicators:
    def __init__(self, server: str) -> None:
        self.db = mongo_client.get_database(settings.MONGODB_NAME)
        self.server = server

    @staticmethod
    def migrate() -> None:
        """
        Cria as condições de banco para os indicadores.
        """
        try:
            async def migrate():
                db = mongo_client.get_database(settings.MONGODB_NAME)
                quoters = db.get_collection(QUOTTERS_COLLECTION)
                requesters = db.get_collection(REGISTERS_COLLECTION)

                try:
                    await quoters.create_index('server', unique=True)
                except Exception as e:
                    LOGGER.debug(e)

                try:
                    await requesters.create_index('server', unique=True)
                except Exception as e:
                    LOGGER.debug(e)

            asyncio.run(migrate())
        except Exception as e:
            raise e

    async def q_usage(self, username: str) -> None:
        """
        Adiciona no contador do comando quotes.
        """
        try:
            LOGGER.info('Add one more quote to %s', username)
            coll = self.db.get_collection(QUOTTERS_COLLECTION)
            quoters = await coll.find_one({ 'server': self.server })
            _documents = dict(quoters) if quoters else None

            if not _documents:
                await coll.insert_one({
                    'server': self.server,
                    username: 1
                })
                return

            _documents.pop('server')

            if not _documents.get(username):
                _documents[username] = 1
            else:
                _documents[username] += 1

            await coll.update_one(
                {'server': self.server},
                _documents,
            )
        except Exception as e:
            raise e

    async def rq_usage(self, username: str) -> None:
        """
        Adiciona no contador do comando randomquote.
        """
        try:
            LOGGER.info('Add one more request for quote to %s', username)
            coll = self.db.get_collection(REGISTERS_COLLECTION)
            requesters = await coll.find_one({ 'server': self.server })
            _documents = dict(requesters) if requesters else None

            if not _documents:  # Servidor sem indicador.
                await coll.insert_one({
                    'server': self.server,
                    username: 1,
                })
                return

            _id = _documents.pop('_id')

            if not _documents.get(username):  # Usuário sem indicador.
                _documents[username] = 1
            else:
                _documents[username] += 1

            await coll.update_one(
                { '_id': _id },
                { '$set': _documents },
            )
        except Exception as e:
            raise e

    async def q_get(self) -> Optional[Dict]:
        """
        Captura o indicador de quotadores do server.
        """
        try:
            LOGGER.info('Getting quoters for server %s', self.server)
            coll = self.db.get_collection(QUOTTERS_COLLECTION)
            requesters = await coll.find_one({ 'server': self.server })

            if not requesters:
                return

            _response = dict(requesters)
            _response.pop('server')
            _response.pop('_id')
            return _response
        except Exception as e:
            LOGGER.error(e)
            raise e

    async def rq_get(self) -> Optional[Dict]:
        """
        Captura o indicador de requisitores do server.
        """
        try:
            LOGGER.info('Getting requesters for server %s', self.server)
            coll = self.db.get_collection(REGISTERS_COLLECTION)
            requesters = await coll.find_one({ 'server': self.server })

            if not requesters:
                return

            _response = dict(requesters)
            _response.pop('server')
            _response.pop('_id')
            return _response
        except Exception as e:
            raise e
