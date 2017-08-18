from logging import getLogger

from django.core.management.base import BaseCommand

from news_scraper.scraper.twitter import TwitterScraper

logger = getLogger(__name__)


class Command(BaseCommand):
    help = 'Runs scraper with configured plugins'

    def handle(self, *args, **options):

        twitter_scraper = TwitterScraper('@iotatoken')

        twitter_scraper.scrape()
