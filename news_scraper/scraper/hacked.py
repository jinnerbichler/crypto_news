from __future__ import unicode_literals

from logging import getLogger

from scrapy import Spider
# noinspection PyPackageRequirements
from bs4 import BeautifulSoup

from news_scraper.scraper import start_scraping

logger = getLogger(__name__)


class Scraper:
    update_interval = 1  # in minutes (twice a day)

    def __init__(self, identifier, config, notifiers):
        self.identifier = identifier
        self.config = config
        self.notifiers = notifiers

    def scrape(self):
        crawler_config = {'ITEM_PIPELINES': {
            'news_scraper.scraper.pipelines.analyse.AnalysePipeline': 800,
            'news_scraper.scraper.pipelines.news.StoreNewsPipeline': 900}
        }

        start_scraping(spider_config=crawler_config, spiders=[HackedSpider])

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
