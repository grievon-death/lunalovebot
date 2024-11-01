import logging
from datetime import datetime
from typing_extensions import Self, Optional, List

from sqlalchemy import  select, update, delete, insert, text
from sqlalchemy import BigInteger, DateTime, String, Text, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, Session

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

    def create(self) -> None:
        """
        Cria o quote e retorna ele.
        """
        try:
            with Session(sql_engine) as session:
                stmt = insert(Quotes).values(
                    message=self.message,
                    server=self.server,
                    created_by=self.created_by,
                    created_at=self.created_at,
                )
                session.execute(stmt)
                session.commit()
        except Exception as e:
            LOGGER.error('Can not create quote %s.\n%s' % (self, e))
            raise e

        LOGGER.info('Created quote %s', self)

    def get(self, id: int) -> Optional[Self]:
        """
        Retorna um objeto baseado no id.
        """
        try:
            with Session(sql_engine) as session:
                stmt = select(Quotes).where(Quotes.id == id)
                cursor = session.execute(stmt)
                quote = cursor.scalar_one_or_none()
                return quote
        except Exception as e:
            LOGGER.error(e)
            raise e

    def all(self, server: str) -> Optional[List[Self]]:
        """
        Captura todos os quotes.
        """
        if not server:
            LOGGER.warning('Please, insert a server to get all quotes.')
            return []

        try:
            with Session(sql_engine) as session:
                stmt = select(Quotes).where(server == self.server)
                cursor  = session.execute(stmt)
                response = cursor.scalars().all()
            return response
        except Exception as e:
            LOGGER.error('Can not get all cotes cause: %s', e)
            raise e

    def get_ids_by_server(self, server: str) -> List[str]:
        """
        Retorna uma lista de IDs baseado no servidor.
        """
        if not server:
            LOGGER.warning('Please, insert a server to get quotes IDs.')
            return

        try:
            with Session(sql_engine) as session:
                stmt = text(f'''
                    select id
                    from quotes
                    where server = '{server}';
                ''')
                cursor = session.execute(stmt)
                return cursor.scalars().all()
        except Exception as e:
            LOGGER.error(e)
            raise e

    def update(self) -> None:
        """
        Altera um usuário.
        """
        try:
            with Session(sql_engine) as session:
                stmt = update(Quotes)\
                    .where(Quotes.id == self.id)\
                    .values(message=self.message)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            LOGGER.error(e)

    def delete(self, id: Optional[Uuid]) -> None:
        """
        Remove um quote do banco de dados.
        """
        id = self.id if id is None else id

        if not id:
            LOGGER.error('Can not delete id %s', id)

        try:
            with Session(sql_engine) as session:
                stmt = delete(Quotes).where(Quotes.id == id)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            LOGGER.error(e)
        else:
            LOGGER.info('Quote %s is removed.', id)

    @staticmethod
    def migrate() -> None:
        Quotes.metadata.create_all(sql_engine)
