import asyncio
import logging
from datetime import datetime
from typing_extensions import Self, Optional, List

from sqlalchemy import  select, update, delete
from sqlalchemy import DateTime, String, Text, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession as Session

from models import BaseTable, sql_engine


LOGGER = logging.getLogger(__name__)


class Quotes(BaseTable):
    __tablename__ = 'quotes'
    __table_args__ = (Index('quote_srv_idx', 'server'), )

    id: Mapped[Uuid] = mapped_column(Uuid(), primary_key=True)
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

    async def create(self) -> Optional[Self]:
        """
        Cria o quote e retorna ele.
        """
        quote = Quotes(
            message=self.message,
            server=self.server,
            created_by=self.created_by,
            created_at=datetime.now(),
        )

        try:
            async with Session(sql_engine) as session:
                await session.add(quote)
                await session.commit()
        except Exception as e:
            LOGGER.error('Can not create quote %s.\n%s' % (quote, e))
            return

        LOGGER.info('Created quote %s', quote)
        return quote

    async def get(self, id: Uuid) -> Optional[Self]:
        """
        Retorna um objeto baseado no id.
        """    
        try:
            async with Session(sql_engine) as session:
                stmt = select(Quotes).where(Quotes.id == id)
                cursor = await session.execute(stmt)
                quote = cursor.scalar_one_or_none()
        except Exception as e:
            LOGGER.error(e)
            return

        LOGGER.info('Get quote %s', quote)
        return quote

    async def all(self, server: str) -> Optional[List[Self]]:
        """
        Captura todos os quotes.
        """
        if not server:
            LOGGER.warning('Please, insert a server to get all quotes.')
            return []

        try:
            async with Session(sql_engine) as session:
                stmt = select(Quotes).where(server == self.server)
                cursor  = await session.execute(stmt)
                response = cursor.scalars().all()
            return response
        except Exception as e:
            LOGGER.error('Can not get all cotes cause: %s', e)

    async def update(self) -> None:
        """
        Altera um usuário.
        """
        try:
            async with Session(sql_engine) as session:
                stmt = update(Quotes)\
                    .where(Quotes.id == self.id)\
                    .values(message=self.message)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            LOGGER.error(e)

    async def delete(self, id: Optional[Uuid]) -> None:
        """
        Remove um quote do banco de dados.
        """
        id = self.id if id is None else id

        if not id:
            LOGGER.error('Can not delete id %s', id)

        try:
            async with Session(sql_engine) as session:
                stmt = delete(Quotes).where(Quotes.id == id)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            LOGGER.error(e)
        else:
            LOGGER.info('Quote %s is removed.', id)

    @staticmethod
    def migrate() -> None:
        async def migration() -> None:
            async with sql_engine.begin() as session:
                await session.run_sync(Quotes.metadata.create_all)
                await session.commit()
            return
        asyncio.run(migration())
