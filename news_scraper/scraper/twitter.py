from __future__ import unicode_literals

from logging import getLogger

import scrapy
import tweepy
from django.conf import settings
from scrapy.http import Request, Response

from news_scraper.scraper import ScraperBase

logger = getLogger(__name__)


class Scraper(ScraperBase):
    update_interval = settings.TWITTER_UPDATE_INTERVAL

    def __init__(self, identifier, config, notifiers):
        spiders_config = {
            'ITEM_PIPELINES': {
                'news_scraper.scraper.pipelines.twitter.TwitterPipeline': 100,
                'news_scraper.scraper.pipelines.analyse_date.AnalysePipeline': 800
            },
            'DOWNLOADER_MIDDLEWARES': {
                'news_scraper.scraper.twitter.TwitterDownloaderMiddleware': 10
            }
        }
        spiders = [(TwitterSpider, {'linked_coin': identifier,
                                    'config': config,
                                    'notifiers': notifiers})]

        super(Scraper, self).__init__(identifier=identifier, config=config,
                                      notifiers=notifiers, spiders=spiders,
                                      spiders_config=spiders_config)

    def __str__(self):
        return "<TwitterScraper {}>".format(self.identifier)


class TwitterSpider(scrapy.Spider):
    name = "twitter-user-timeline"
    allowed_domains = ["twitter.com"]

    # noinspection PyUnresolvedReferences
    def __init__(self, linked_coin=None, config=None, notifiers=None, *args, **kwargs):
        if not linked_coin or not config or notifiers is None:
            raise scrapy.exceptions.CloseSpider('Invalid arguments...')
        super(TwitterSpider, self).__init__(*args, **kwargs)

        self.linked_coin = linked_coin
        self.notifiers = notifiers
        self.users = config['users']
        self.hashtags = config['hashtags']
        self.excluded_authors = config['exclude_users']
        self.count = 50

    def start_requests(self):
        requests = [TwitterUserTimelineRequest(screen_name=sn, count=self.count)
                    for sn in self.users]
        requests += [TwitterHashtagRequest(hashtag=ht, count=self.count)
                     for ht in self.hashtags]
        return requests

    def parse(self, response):
        for tweet in response.tweets:
            yield {'tweet': tweet}


# noinspection PyUnusedLocal
class TwitterUserTimelineRequest(Request):
    def __init__(self, *args, **kwargs):
        self.screen_name = kwargs.pop('screen_name', None)
        self.count = kwargs.pop('count', None)
        super(TwitterUserTimelineRequest, self).__init__('http://twitter.com',
                                                         dont_filter=True,
                                                         **kwargs)


# noinspection PyUnusedLocal
class TwitterHashtagRequest(Request):
    def __init__(self, *args, **kwargs):
        self.hashtag = kwargs.pop('hashtag', None)
        self.count = kwargs.pop('count', None)
        super(TwitterHashtagRequest, self).__init__('http://twitter.com',
                                                    dont_filter=True,
                                                    **kwargs)


class TwitterResponse(Response):
    def __init__(self, *args, **kwargs):
        self.tweets = kwargs.pop('tweets', None)
        super(TwitterResponse, self).__init__('http://twitter.com', *args, **kwargs)


# noinspection PyUnusedLocal,PyMethodMayBeStatic
class TwitterDownloaderMiddleware(object):
    def __init__(self, api_key, api_secret, access_token_key, access_token_secret):
        # setup authentication
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token_key, access_token_secret)
        self.api = tweepy.API(auth)

    @classmethod
    def from_crawler(cls, crawler):
        api_key = settings.TWITTER_API_KEY
        api_secret = settings.TWITTER_API_SECRET
        access_token_key = settings.TWITTER_ACCESS_TOKEN
        access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET
        return cls(api_key, api_secret, access_token_key, access_token_secret)

    def process_request(self, request, spider):

        # timeline
        tweets = []
        if isinstance(request, TwitterUserTimelineRequest):
            tweets = tweepy.Cursor(self.api.user_timeline,
                                   id=request.screen_name,
                                   count=request.count)
        # hashtags
        elif isinstance(request, TwitterHashtagRequest):
            tweets = tweepy.Cursor(self.api.search,
                                   q=request.hashtag,
                                   count=request.count)

        return TwitterResponse(tweets=[t for t in tweets.items(limit=request.count)])

    def process_response(self, request, response, spider):
        return response
