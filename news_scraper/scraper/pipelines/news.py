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

            return {'title': news_article.title,
                    'text': news_article.text,
                    'author': news_article.author,
                    'created_at': news_article.model_created_at,
                    'url': news_article.url,
                    'source': news_article}

        except IntegrityError:
            pass

        raise DropItem("Duplicate item found: %s" % item)
