from logging import getLogger
from multiprocessing import Process
from django.conf import settings
from scrapy.crawler import CrawlerProcess

from news_scraper.notifier import get_notifier

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


def notify_scrape_error(url, item):
    error_notifier = get_notifier(notifier_id='dev_notifier')
    if error_notifier:
        error_notifier.notify(title='Error while scraping: {}'.format(url),
                              message='Item {}'.format(item),
                              url=url)


class ScraperBase:
    def __init__(self, identifier, config, notifiers, spiders,
                 spiders_config, default_interval):
        self.identifier = identifier
        self.config = config
        self.notifiers = notifiers
        self.update_interval = config.get('update_interval', default_interval)

        self.spiders = spiders
        self.spiders_config = spiders_config

        logger.info('Initialized {}'.format(self))

    def scrape(self):
        start_scraping(spider_config=self.spiders_config, spiders=self.spiders)
