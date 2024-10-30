import asyncio
import logging
import time
from datetime import datetime

from sqlalchemy import text

from models import sql_engine
from models.indicator import Indicators

LOGGER = logging.getLogger(__name__)


def indicator() -> None:
    """
    Processa os indicadores a cada 1h.
    """
    async def start():
        stmt = text("""
            select distinct server
            from quotes;
        """)

        while True:
            LOGGER.info('Indicator daemon start at %s', datetime.now().isoformat())
            async with sql_engine.begin() as session:
                cursor = await session.execute(stmt)
                response = cursor.scalars().all()

            for server in response:
                ind = Indicators(server)
                await ind.calculate_quoters()

            LOGGER.info('Indicator daemon finished at %s', datetime.now().isoformat())
            time.sleep(3600)

    asyncio.run(start())
