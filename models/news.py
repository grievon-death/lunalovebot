import logging
from typing import Dict, List, Self

import requests
from bs4 import BeautifulSoup

from settings import BBC_NEWS_URL

LOGGER = logging.getLogger(__name__)


class News:
    """
    Realiza web scrapping para capturar notícias jornalisticas.
    """
    new: str
    date: str
    link: str
    image: str

    def __init__(self, source='bbc', **kwargs: Dict):
        self.source = source

        if kwargs:
            try:
                self.new = kwargs['new']
                self.date = kwargs['date']
                self.link = kwargs['link']
                self.image = kwargs['image']
            except KeyError as e:
                LOGGER.error(e)
                raise e

    async def _get_from_bbc(self) -> List[Dict]:
        """
        Captura notícias da BBC.
        """
        html = requests.get(BBC_NEWS_URL).content
        soup = BeautifulSoup(html, 'html.parser')
        raw_html = soup.find('ul', class_='bbc-k6wdzo')
        raw_news = raw_html.contents
        news = []

        for new in raw_news:
            _new = new.find('h2').text
            _date = new.find('time').text
            _link = new.find('a').attrs.get('href')
            _img = new.find('div', class_='promo-image').find('img').attrs.get('src')
            news.append({
                'new': _new,
                'date': _date,
                'link': _link,
                'image': _img
            })

        return news

    async def get(self) -> List[Self]:
        """
        Captura notícias da fonte.
        """
        if self.source == 'bbc':
            data = await self._get_from_bbc()
            return [News(**d) for d in data]
        return []
