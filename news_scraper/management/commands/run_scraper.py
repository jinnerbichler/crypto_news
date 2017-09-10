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
        for scraper in scrapers:
            perform_scraping(scraper=scraper)
            schedule_scraping(scraper=scraper)


def init_scrapers(notifiers):
    scrapers = []
    for identifier, token_config in settings.SCRAPERS.items():

        scraper_notifiers = [notifiers[n] for n in token_config['notifiers']]
        for scraper_type, scraper_config in token_config['scrapers'].items():
            if scraper_type != 'notifier':
                # loading module of scraper
                scraper_module_path = 'news_scraper.scraper.{}'.format(scraper_type)
                logger.info('Loading scraper {}'.format(scraper_module_path))
                scraper_module = importlib.import_module(scraper_module_path)

                # instantiate scraper
                scraper = scraper_module.Scraper(identifier=identifier,
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


def schedule_scraping(scraper):

    def update():
        perform_scraping(scraper=scraper)
        schedule_scraping(scraper=scraper)

    ohlc_interval = scraper.update_interval
    next_time = datetime.now() + timedelta(seconds=ohlc_interval * 60)
    logger.info('Scheduling next scraping of {} at {} (UTC)'.format(scraper, next_time))
    threading.Timer((next_time - datetime.now()).total_seconds(), update).start()


# noinspection PyBroadException
def perform_scraping(scraper):
    try:
        scraper.scrape()
    except:
        logger.exception('Error while scraping {}'.format(scraper))
