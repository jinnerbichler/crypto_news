from __future__ import unicode_literals
from logging import getLogger
from django.conf import settings
from multiprocessing import Process
from scrapy import Spider
from scrapy.crawler import CrawlerProcess, CrawlerRunner
# noinspection PyPackageRequirements
from bs4 import BeautifulSoup
from twisted.internet import reactor

logger = getLogger(__name__)


class Scraper:
    update_interval = 1  # in minutes (twice a day)

    def __init__(self, identifier, config, notifiers):
        self.identifier = identifier
        self.config = config
        self.notifiers = notifiers

    def scrape(self):
        crawler_config = settings.CRAWLER_DEFAULTS.copy()
        crawler_config['ITEM_PIPELINES'] = {
            # 'news_scraper.scraper.pipelines.analyse_news.AnalyseNewsPipeline': 800,
            'news_scraper.scraper.pipelines.store_news.StoreNewsPipeline': 900
        }

        # start crawling
        def start_crawling():
            process = CrawlerProcess(crawler_config)
            process.crawl(HackedSpider)
            process.start(stop_after_crawl=True)

        p = Process(target=start_crawling)
        p.start()
        p.join()

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
