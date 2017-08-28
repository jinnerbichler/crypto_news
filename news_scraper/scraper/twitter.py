from __future__ import unicode_literals
from logging import getLogger

import time
import re
from django.conf import settings
from django.utils.timezone import make_aware, utc
from news_scraper.models import Tweet

import tweepy

logger = getLogger(__name__)


class Scraper:
    def __init__(self, token_name, config, notifiers):
        self.token_name = token_name
        self.users = config['users']
        self.hashtags = config['hashtags']
        self.notifiers = notifiers

        # setup authentication
        auth = tweepy.OAuthHandler(settings.TWITTER_API_KEY,
                                   settings.TWITTER_API_SECRET)
        auth.set_access_token(settings.TWITTER_ACCESS_TOKEN,
                              settings.TWITTER_ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

        logger.info('{} initialised'.format(self))

    def scrape(self):
        logger.info('{} start scraping'.format(self))

        # search for tweets of users
        for user in self.users:
            logger.info('{} scraping {}'.format(self, user))
            cursor = tweepy.Cursor(self.api.user_timeline, id=user, count=50)
            for tweet in cursor.items(limit=50):
                self._progress_tweet(tweet)
            time.sleep(0.5)

        # search for specific hashtags
        for hashtag in self.hashtags:
            logger.info('{} scraping {}'.format(self, hashtag))
            cursor = tweepy.Cursor(self.api.search, q=hashtag, count=50)
            for tweet in cursor.items(limit=50):
                self._progress_tweet(tweet)
            time.sleep(0.5)

    def _progress_tweet(self, tweet):

        # filter tweet
        is_new = not Tweet.objects.filter(identifier=tweet.id,
                                          linked_token=self.token_name).exists()
        is_retweet = tweet.retweeted or ('RT @' in tweet.text)
        contains_chinese = re.search(u'[\u4e00-\u9fff]', tweet.text)  # ToDo: translate

        if is_new and not is_retweet and not contains_chinese:
            tweet_to_store = Tweet(created_at=make_aware(tweet.created_at, utc),
                                   creator=tweet.author.screen_name,
                                   text=tweet.text,
                                   identifier=tweet.id,
                                   linked_token=self.token_name)

            for notifier in self.notifiers:
                notifier.notify(
                    title='New tweet from {}'.format(tweet.author.screen_name),
                    message=tweet.text,
                    url=construct_twitter_link(tweet))

            tweet_to_store.save()

            logger.info('Found new tweet {}'.format(tweet_to_store))

    def __str__(self):
        return "<TwitterScraper {}>".format(self.token_name)


def construct_twitter_link(status):
    return 'https://twitter.com/statuses/{}'.format(status.id)
