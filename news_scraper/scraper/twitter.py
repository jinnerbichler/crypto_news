from __future__ import unicode_literals
from logging import getLogger
from django.conf import settings

import tweepy

logger = getLogger(__name__)


class TwitterScraper:
    def __init__(self, user):
        self.user = user

        # setup authentication
        auth = tweepy.OAuthHandler(settings.TWITTER_API_KEY,
                                   settings.TWITTER_API_SECRET)
        auth.set_access_token(settings.TWITTER_ACCESS_TOKEN,
                              settings.TWITTER_ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

        logger.info('{} initialised'.format(self))

    def scrape(self):
        logger.info('{} start scraping'.format(self))

        for status in self.api.user_timeline(self.user):
            print(status.text)

    def __str__(self):
        return "<TwitterScraper user: '{}'>".format(self.user)
