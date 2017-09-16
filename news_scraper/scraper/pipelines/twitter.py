import logging
import re

from django.conf import settings
from django.db import IntegrityError
from django.utils.timezone import make_aware, utc
from scrapy.exceptions import DropItem

from news_scraper.models import Tweet
from news_scraper.notifier import notify_all

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class TwitterPipeline(object):
    """Pipeline that filters, pre-processes and stores Twitter items"""

    def process_item(self, item, spider):

        tweet = item['tweet']

        # filter tweet
        is_retweet = tweet.retweeted or ('RT @' in tweet.text)
        contains_chinese = re.search(u'[\u4e00-\u9fff]', tweet.text)  # ToDo: translate
        screen_name = tweet.author.screen_name
        is_author_excluded = '@{}'.format(screen_name).lower() in spider.excluded_authors
        followers_count = tweet.author.followers_count
        has_enough_followers = followers_count > settings.TWITTER_FOLLOWERS_THRESH

        if not is_retweet \
                and not contains_chinese \
                and not is_author_excluded \
                and has_enough_followers:
            tweet_to_store = Tweet(created_at=make_aware(tweet.created_at, utc),
                                   creator=tweet.author.screen_name,
                                   text=tweet.text,
                                   identifier=tweet.id,
                                   linked_token=spider.linked_coin)
            try:
                tweet_to_store.save()

                logger.info('Found new Tweet {}'.format(tweet_to_store))

                # trigger notifications
                notify_all(notifiers=spider.notifiers,
                           title='New Tweet from {}'.format(tweet.author.screen_name),
                           message=tweet.text,
                           url=construct_twitter_link(tweet))

                return {'title': 'Tweet from {}'.format(tweet_to_store.creator),
                        'text': tweet.text,
                        'author': tweet.author.screen_name,
                        'created_at': tweet.created_at,
                        'url': construct_twitter_link(tweet),
                        'source': tweet_to_store,
                        'linked_coin': spider.linked_coin}

            except IntegrityError:
                pass

        raise DropItem("Dropping tweet: %s" % item)


def construct_twitter_link(status):
    return 'https://twitter.com/statuses/{}'.format(status.id)
