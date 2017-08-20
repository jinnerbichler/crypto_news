from __future__ import unicode_literals
from logging import getLogger
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
            cursor = tweepy.Cursor(self.api.user_timeline, id=user, count=50)
            for item in cursor.items(limit=50):
                self._progress_item(item)

        # search for specific hashtags
        for hashtag in self.hashtags:
            cursor = tweepy.Cursor(self.api.search, q=hashtag, count=50)
            for item in cursor.items(limit=50):
                self._progress_item(item)

    def _progress_item(self, item):

        is_new = not Tweet.objects.filter(identifier=item.id,
                                          linked_token=self.token_name).exists()
        if is_new:
            tweet = Tweet(created_at=make_aware(item.created_at, utc),
                          creator=item.author.screen_name,
                          text=item.text,
                          identifier=item.id,
                          linked_token=self.token_name)
            tweet.save()

            for notifier in self.notifiers:
                notifier.notify(title='New tweet from {}'.format(item.author.screen_name),
                                message=item.text,
                                url=construct_twitter_link(item))

    def __str__(self):
        return "<TwitterScraper {}>".format(self.token_name)


def construct_twitter_link(status):
    return 'https://twitter.com/statuses/{}'.format(status.id)
