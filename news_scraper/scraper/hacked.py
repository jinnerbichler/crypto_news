from __future__ import unicode_literals

from logging import getLogger

from django.conf import settings
from scrapy import Spider
# noinspection PyPackageRequirements
from bs4 import BeautifulSoup

from news_scraper.scraper import ScraperBase

logger = getLogger(__name__)


class Scraper(ScraperBase):
    update_interval = settings.NEWS_UPDATE_INTERVAL

    def __init__(self, **kwargs):
        spiders_config = {
            'ITEM_PIPELINES': {
                'news_scraper.scraper.pipelines.news.StoreNewsPipeline': 800,
                'news_scraper.scraper.pipelines.analyse_date.AnalysePipeline': 900,
            }
        }
        spiders = [(HackedSpider, {})]
        super(Scraper, self).__init__(**kwargs, spiders=spiders,
                                      spiders_config=spiders_config)

    def __str__(self):
        return "<HackedComScraper {}>".format(self.identifier)


# noinspection PyMethodMayBeStatic
class HackedSpider(Spider):
    name = "hacked.com"

    start_urls = ['https://hacked.com/']

    def parse(self, response):
        for article in response.css('.posts article'):
            href = article.css('header h1 a::attr(href)').extract_first()
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        article_raw = response.css('.posts article .postbody').extract_first()
        article_soup = BeautifulSoup(article_raw, 'lxml')

        # remove ads
        for div in article_soup.find_all('div', {'class': 'code-block'}):
            div.decompose()

        # remove tables
        for table in article_soup.find_all('table'):
            table.decompose()

        item = {
            'crawler_id': self.name,
            'title': response.css('#posttitle::text').extract_first().strip(),
            'author': response.css('.postauthor a::text').extract_first(),
            'text': article_soup.get_text().strip(),
            'url': response.url,
            'creator_url': self.start_urls[0]
        }

        # check if item is valid
        if any(v is None for v in item.values()):
            return  # ToDo: shoot message

        yield item
