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

        tweet_item = item['tweet']

        # filter tweet
        is_retweet = tweet_item.retweeted or ('RT @' in tweet_item.text)
        contains_chinese = re.search(u'[\u4e00-\u9fff]',
                                     tweet_item.text)  # ToDo: translate
        screen_name = tweet_item.author.screen_name
        is_author_excluded = '@{}'.format(screen_name).lower() in spider.excluded_authors
        followers_count = tweet_item.author.followers_count
        has_enough_followers = followers_count > settings.TWITTER_FOLLOWERS_THRESH

        if not is_retweet \
                and not contains_chinese \
                and not is_author_excluded \
                and has_enough_followers:
            tweet = Tweet(created_at=make_aware(tweet_item.created_at, utc),
                          creator=tweet_item.author.screen_name,
                          text=tweet_item.text,
                          identifier=tweet_item.id,
                          linked_token=spider.linked_coin)
            try:
                tweet.save()

                logger.info('Found new Tweet {}'.format(tweet))

                # trigger notifications
                notify_all(notifiers=spider.hotness_notifiers,
                           title='New Tweet from {}'.format(
                               tweet_item.author.screen_name),
                           message=tweet_item.text,
                           url=construct_twitter_link(tweet_item))

                return {'title': 'Tweet from {}'.format(tweet.creator),
                        'text': tweet_item.text,
                        'author': tweet_item.author.screen_name,
                        'created_at': tweet_item.created_at,
                        'url': construct_twitter_link(tweet_item),
                        'source': tweet,
                        'linked_coin': spider.linked_coin}

            except IntegrityError as ex:
                try:
                    tweet = Tweet.objects.get(identifier=tweet_item.id,
                                              linked_token=spider.linked_coin)

                    # check for hotness
                    is_hot = is_tweet_hot(tweet_item)
                    if not tweet.is_hot and is_hot:
                        # shoot notifications
                        message = 'FAV: {}, RETW: {}\n{}'.format(
                            tweet_item.favorite_count,
                            tweet_item.retweet_count,
                            tweet.text)
                        title = 'Hot Tweet detected for {}'.format(spider.linked_coin)
                        notify_all(notifiers=spider.hotness_notifiers,
                                   title=title,
                                   message=message,
                                   url=construct_twitter_link(tweet_item))
                        logger.info(
                            'Found new hot tweet ({}) from {}'.format(tweet.identifier,
                                                                      tweet.creator))

                        # update stored tweet
                        tweet.is_hot = is_hot
                        tweet.save()
                except Tweet.DoesNotExist as e:
                    logger.error(
                        'Cannot find Tweet {} in database!'.format(tweet_item.id))

        raise DropItem("Dropping tweet: %s" % item)


def construct_twitter_link(status):
    return 'https://twitter.com/statuses/{}'.format(status.id)


def is_tweet_hot(tweet_item):
    hot_fav_count = tweet_item.favorite_count > settings.TWITTER_HOTNESS_LIKES_THRESH
    hot_retweet_count = tweet_item.retweet_count > settings.TWITTER_HOTNESS_RETWEET_THRESH
    return hot_fav_count and hot_retweet_count
