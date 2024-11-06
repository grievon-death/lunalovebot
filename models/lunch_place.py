import logging
from datetime import datetime
from typing_extensions import Self, Optional, List
from random import choice

from sqlalchemy import  select, update, delete, insert, text
from sqlalchemy import BigInteger, DateTime, String, Text, Uuid, Index
from sqlalchemy.orm import Mapped, mapped_column, Session

from models import BaseTable, sql_engine

LOGGER = logging.getLogger(__name__)


class LunchPlace(BaseTable):
    __tablename__ = 'lunch_place'
    __table_args__ = (Index('lunch_place_srv_idx', 'server'), )

    id: Mapped[BigInteger] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    place: Mapped[String] = mapped_column(Text(), nullable=False)
    server: Mapped[String] = mapped_column(String(50), nullable=False)
    created_by: Mapped[String] = mapped_column(String(50), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(), nullable=False, default=datetime.now())

    def __repr__(self) -> str:
        return f'LunchPlace(id: {self.id}, '\
            f'place: {self.place}, '\
            f'server: {self.server}'\
            f'created_by: {self.created_by}, '\
            f'created_at: {self.created_at})'

    def create(self) -> None:
        """
        Cria o local de almoço e retorna ele.
        """
        try:
            with Session(sql_engine) as session:
                stmt = insert(LunchPlace).values(
                    place=self.place,
                    server=self.server,
                    created_by=self.created_by,
                    created_at=self.created_at,
                )
                session.execute(stmt)
                session.commit()
        except Exception as e:
            LOGGER.error('Can not create lunch place %s.\n%s' % (self, e))
            raise e

        LOGGER.info('Created lunch place %s', self)

    def get(self, id: int) -> Optional[Self]:
        """
        Retorna um objeto baseado no id.
        """
        try:
            with Session(sql_engine) as session:
                stmt = select(LunchPlace).where(LunchPlace.id == id)
                cursor = session.execute(stmt)
                quote = cursor.scalar_one_or_none()
                return quote
        except Exception as e:
            LOGGER.error(e)
            raise e

    def all(self, server: str) -> Optional[List[Self]]:
        """
        Captura todos os locais de almoço.
        """
        if not server:
            LOGGER.warning('Please, insert a server to get all lunch places.')
            return []

        try:
            with Session(sql_engine) as session:
                stmt = select(LunchPlace).where(server == self.server)
                cursor  = session.execute(stmt)
                response = cursor.scalars().all()
            return response
        except Exception as e:
            LOGGER.error('Can not get all lunch places cause: %s', e)
            raise e

    def get_ids_by_server(self, server: str) -> List[str]:
        """
        Retorna uma lista de IDs baseado no servidor.
        """
        if not server:
            LOGGER.warning('Please, insert a server to get lunch place IDs.')
            return

        try:
            with Session(sql_engine) as session:
                stmt = text(f'''
                    select id
                    from lunch_place
                    where server = '{server}';
                ''')
                cursor = session.execute(stmt)
                return cursor.scalars().all()
        except Exception as e:
            LOGGER.error(e)
            raise e

    def update(self) -> None:
        """
        Altera um local de almoço.
        """
        try:
            with Session(sql_engine) as session:
                stmt = update(LunchPlace)\
                    .where(LunchPlace.id == self.id)\
                    .values(place=self.place)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            LOGGER.error(e)

    def delete(self, id: Optional[Uuid]) -> None:
        """
        Remove um local de almoço do banco de dados.
        """
        id = self.id if id is None else id

        if not id:
            LOGGER.error('Can not delete id %s', id)

        try:
            with Session(sql_engine) as session:
                stmt = delete(LunchPlace).where(LunchPlace.id == id)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            LOGGER.error(e)
        else:
            LOGGER.info('Lunch place %s is removed.', id)

    @staticmethod
    def migrate() -> None:
        LunchPlace.metadata.create_all(sql_engine)

    @staticmethod
    def get_random_intro() -> String:
        intros = [
            'Hoje eu tô com vontade de',
            'Só quero almoçar se for',
            'Tô com fome de',
            'Ah, sei lá! Pode ser',
            'Partiu',
            'Só porque vocês pediram pra eu decidir, vai ser',
            'Gente, eu nem como! Sou só um bot do discord! Querem uma sugestão? Beleza:',
            'Eu vou decidir dessa vez, mas na próxima vocês se viram:',
            'Nossa, sabe um lugar que faz tempo que a gente não vai?',
            'Na falta de opções melhores, pode ser',
            'Eu já tava pedindo um Ifood aqui, mas então pode ser',
            'Gente, eu não vou! Eu trouxe marmita hoje. Mas se fosse pra escolher um lugar, eu escolheria',
            'Como estão de grana? Tava com vontade de',
            'Por mim pode ser qualquer lugar, desde que seja',
            'Só digo uma coisa:',
            'Eu queria ir no Outback, mas como vocês não vão querer, pode ser',
            'Minha nutricionista recomendou',
            'Meu psiquiatra acha que eu devo escolher',
            'Já dizia o salmo 4:20 - se queres almoçar, não suba a montanha nem atravesse o rio! Deves ir direto para',
            'Por motivos pessoais que não posso informar, hoje tem que ser',
            'Acabei de perguntar pro ChatGPT um lugar pra almoçar, e ele disse'
        ]

        return choice(intros)