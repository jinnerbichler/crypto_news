import threading
from datetime import timedelta, datetime
from logging import getLogger
from django.core.management.base import BaseCommand
from django.conf import settings
import importlib

logger = getLogger(__name__)


class Command(BaseCommand):
    help = 'Runs scrapers with configured plugins'

    def handle(self, *args, **options):
        # initialise notifier
        notifiers = init_notifiers()

        # initialise scrapers
        scrapers = init_scrapers(notifiers=notifiers)

        # perform periodic scraping
        perform_scraping(scrapers=scrapers)
        schedule_scraping(scrapers=scrapers)


def init_scrapers(notifiers):
    scrapers = []
    for scraped_token, token_config in settings.SCRAPERS.items():

        scraper_notifiers = [notifiers[n] for n in token_config['notifiers']]
        for scraper_type, scraper_config in token_config['scrapers'].items():
            if scraper_type != 'notifier':
                # loading module of scraper
                scraper_module_path = 'news_scraper.scraper.{}'.format(scraper_type)
                logger.info('Loading scraper {}'.format(scraper_module_path))
                scraper_module = importlib.import_module(scraper_module_path)

                # instantiate scraper
                scraper = scraper_module.Scraper(token_name=scraped_token,
                                                 config=scraper_config,
                                                 notifiers=scraper_notifiers)

                scrapers.append(scraper)

    return scrapers


def init_notifiers():
    notifiers = {}
    for notifier_id, notifier_config in settings.NOTIFIERS.items():
        notifier_path = 'news_scraper.notifier.{}'.format(notifier_config['type'])
        notifier_module = importlib.import_module(notifier_path)
        notifiers[notifier_id] = notifier_module.Notifier(identifier=notifier_id,
                                                          config=notifier_config)
    return notifiers


def schedule_scraping(scrapers):
    ohlc_interval = 15  # in minutes
    next_time = datetime.now() + timedelta(seconds=ohlc_interval * 60)

    def update():
        perform_scraping(scrapers=scrapers)
        schedule_scraping(scrapers=scrapers)

    threading.Timer((next_time - datetime.now()).total_seconds(), update).start()
    logger.info('Scheduled next scraping at {} (UTC)'.format(next_time))


# noinspection PyBroadException
def perform_scraping(scrapers):
    for scraper in scrapers:
        try:
            scraper.scrape()
        except:
            logger.exception('Error while scraping {}'.format(scraper))
