from logging import getLogger
from multiprocessing import Process
from django.conf import settings
from scrapy.crawler import CrawlerProcess

logger = getLogger(__name__)


def start_scraping(spider_config, spiders):
    crawler_config = settings.CRAWLER_DEFAULTS.copy()
    crawler_config.update(spider_config)

    # start crawling in dedicated process (due to Twisted lib...)
    def start_crawling():
        process = CrawlerProcess(crawler_config)
        for spider, kwargs in spiders:
            process.crawl(spider, **kwargs)
        process.start(stop_after_crawl=True)

    p = Process(target=start_crawling)
    p.start()
    p.join()


class ScraperBase:
    def __init__(self, identifier, config, notifiers, spiders, spiders_config):
        self.identifier = identifier
        self.config = config
        self.notifiers = notifiers

        self.spiders = spiders
        self.spiders_config = spiders_config

        logger.info('Initialized {}'.format(self))

    def scrape(self):
        start_scraping(spider_config=self.spiders_config, spiders=self.spiders)
