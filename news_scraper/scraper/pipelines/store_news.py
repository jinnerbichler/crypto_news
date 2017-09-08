from django.db import IntegrityError
import logging
from news_scraper.models import NewsArticle
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class StoreNewsPipeline(object):
    """Pipeline that stores news items persistently and drops already stored items"""

    def process_item(self, item, spider):
        try:
            news_article = NewsArticle(**item)
            news_article.save()
            logger.info('Saved {}'.format(news_article))
        except IntegrityError:
            raise DropItem("Duplicate item found: %s" % item)

        return item
