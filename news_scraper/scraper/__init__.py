from multiprocessing import Process
from django.conf import settings
from scrapy.crawler import CrawlerProcess


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
