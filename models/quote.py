import logging
from datetime import datetime
from typing_extensions import Self, Optional, List

from sqlalchemy import  select, update, delete, insert, text
from sqlalchemy import BigInteger, DateTime, String, Text, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from models import BaseTable, sql_engine

LOGGER = logging.getLogger(__name__)


class Quotes(BaseTable):
    __tablename__ = 'quotes'
    __table_args__ = (Index('quote_srv_idx', 'server'), )

    id: Mapped[BigInteger] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    message: Mapped[Text] = mapped_column(Text(), nullable=False)
    server: Mapped[String] = mapped_column(String(50), nullable=False)
    created_by: Mapped[String] = mapped_column(String(50), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(), nullable=False, default=datetime.now())

    def __repr__(self) -> str:
        return f'Quote(id: {self.id}, '\
            f'message: {self.message}, '\
            f'server: {self.server}'\
            f'created_by: {self.created_by}, '\
            f'created_at: {self.created_at})'

    async def create(self) -> None:
        """
        Cria o quote e retorna ele.
        """
        try:
            async with AsyncSession(sql_engine) as session:
                stmt = insert(Quotes).values(
                    message=self.message,
                    server=self.server,
                    created_by=self.created_by,
                    created_at=self.created_at,
                )
                cursor = await session.execute(stmt)
                await session.commit()
                self.id = cursor.inserted_primary_key[0]
        except Exception as e:
            LOGGER.error('Can not create quote %s.\n%s' % (self, e))
            raise e

        LOGGER.info('Created quote %s', self)

    async def get(self, id: int, server: str) -> Optional[Self]:
        """
        Retorna um objeto baseado no id.
        """
        try:
            async with AsyncSession(sql_engine) as session:
                stmt = select(Quotes).where(Quotes.id == id).where(Quotes.server == server)
                cursor = await session.execute(stmt)
                quote = cursor.scalar_one_or_none()
                return quote
        except Exception as e:
            LOGGER.error(e)
            raise e

    async def all(self, server: str) -> Optional[List[Self]]:
        """
        Captura todos os quotes.
        """
        if not server:
            LOGGER.warning('Please, insert a server to get all quotes.')
            return []

        try:
            async with AsyncSession(sql_engine) as session:
                stmt = select(Quotes).where(server == self.server)
                cursor  = await session.execute(stmt)
                response = cursor.scalars().all()
            return response
        except Exception as e:
            LOGGER.error('Can not get all cotes cause: %s', e)
            raise e

    async def get_ids_by_server(self, server: str, not_in: List[int]) -> List[str]:
        """
        Retorna uma lista de IDs baseado no servidor.
        """
        if not server:
            LOGGER.warning('Please, insert a server to get quotes IDs.')
            return

        stmt = '''
            select id
            from quotes
            where server = :server
        '''
        params = {
            'server': server
        }

        if not_in:
            stmt += ' and id not in :not_in;'
            params['not_in'] = tuple(not_in)

        try:
            async with AsyncSession(sql_engine) as session:
                cursor = await session.execute(text(stmt), params=params)
                return cursor.scalars().all()
        except Exception as e:
            LOGGER.error(e)
            raise e

    async def update(self) -> None:
        """
        Altera um usuário.
        """
        try:
            async with AsyncSession(sql_engine) as session:
                stmt = update(Quotes)\
                    .where(Quotes.id == self.id)\
                    .values(message=self.message)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            LOGGER.error(e)

    async def delete(self) -> None:
        """
        Remove um quote do banco de dados.
        """
        try:
            async with AsyncSession(sql_engine) as session:
                stmt = delete(Quotes).where(Quotes.id == self.id)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            LOGGER.error(e)
        else:
            LOGGER.info('Quote %s is removed.', self.id)

    @staticmethod
    async def migrate() -> None:
        async with sql_engine.begin() as session:
            await session.run_sync(Quotes.metadata.create_all)
