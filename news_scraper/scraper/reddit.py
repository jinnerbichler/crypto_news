import time
from logging import getLogger

import collections
import scrapy
from django.conf import settings
from praw import Reddit
from scrapy import Request
from scrapy.http import Response

from news_scraper.scraper import ScraperBase

logger = getLogger(__name__)


class Scraper(ScraperBase):
    def __init__(self, identifier, config, notifiers):
        spiders_config = {
            'ITEM_PIPELINES': {
                'news_scraper.scraper.pipelines.reddit.RedditPipeline': 100,
                'news_scraper.scraper.pipelines.analyse_date.AnalysePipeline': 800
            },
            'DOWNLOADER_MIDDLEWARES': {
                'news_scraper.scraper.reddit.RedditDownloaderMiddleware': 10
            }
        }
        spiders = [(RedditSpider, {'linked_coin': identifier,
                                   'config': config,
                                   'notifiers': notifiers})]

        super(Scraper, self).__init__(identifier=identifier, config=config,
                                      notifiers=notifiers, spiders=spiders,
                                      spiders_config=spiders_config,
                                      default_interval=settings.REDDIT_UPDATE_INTERVAL)

    def __str__(self):
        return "<RedditScraper {}>".format(self.identifier)


class RedditSpider(scrapy.Spider):
    name = 'reddit-submissions'
    allowed_domains = ['reddit.com']

    # noinspection PyUnresolvedReferences
    def __init__(self, linked_coin=None, config=None, notifiers=None, *args, **kwargs):
        if not linked_coin or not config or notifiers is None:
            raise scrapy.exceptions.CloseSpider('Invalid arguments...')
        super(RedditSpider, self).__init__(*args, **kwargs)

        self.linked_coin = linked_coin
        self.notifiers = notifiers
        self.subreddits = config['subreddits']

    def start_requests(self):
        return [SubredditRequest(subreddit=sr) for sr in self.subreddits]

    def parse(self, response):
        for submission in response.submissions:
            yield {'submission': submission,
                   'authors': response.authors}


# noinspection PyUnusedLocal
class SubredditRequest(Request):
    def __init__(self, *args, **kwargs):
        self.subreddit = kwargs.pop('subreddit', None)
        super(SubredditRequest, self).__init__(
            'https://www.reddit.com/r/{}'.format(self.subreddit),
            dont_filter=True, **kwargs)


# noinspection PyUnusedLocal
class SubredditResponse(Response):
    def __init__(self, *args, **kwargs):
        self.subreddit = kwargs.pop('subreddit', None)
        self.submissions = kwargs.pop('submissions', None)
        self.authors = kwargs.pop('authors', None)
        super(SubredditResponse, self).__init__(
            'https://www.reddit.com/r/{}'.format(self.subreddit), *args, **kwargs)


Submission = collections.namedtuple('Submission', 'submission comments')


# noinspection PyUnusedLocal
class RedditDownloaderMiddleware(object):
    def __init__(self, client_id, client_secret, username, password, count):
        # setup api with authentication
        self.api = Reddit(client_id=client_id,
                          client_secret=client_secret,
                          username=username,
                          password=password,
                          user_agent='testscript by /u/jinnerbichler')
        self.count = count

    @classmethod
    def from_crawler(cls, crawler):
        client_id = settings.REDDIT_CLIENT_ID
        client_secret = settings.REDDIT_CLIENT_SECRET
        username = settings.REDDIT_USERNAME
        password = settings.REDDIT_PASSWORD
        count = settings.REDDIT_SUBMISSION_LIMIT
        return cls(client_id, client_secret, username, password, count)

    def process_request(self, request, spider):

        fetched_submissions = []
        authors = {}

        if isinstance(request, SubredditRequest):

            # fetch submissions
            subreddit = self.api.subreddit(request.subreddit).hot(limit=self.count)
            for submission in subreddit:

                new_submission = Submission(submission=submission, comments=[])

                # pre-fetch comments
                submission.comment_sort = 'new'
                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list():
                    authors[comment.id] = comment.author
                    new_submission.comments.append(comment)

                fetched_submissions.append(new_submission)

                time.sleep(0.1)

            return SubredditResponse(subreddit=request.subreddit,
                                     submissions=fetched_submissions,
                                     authors=authors)

    # noinspection PyMethodMayBeStatic
    def process_response(self, request, response, spider):
        return response
