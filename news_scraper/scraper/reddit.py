from django.conf import settings
from praw import Reddit
from datetime import datetime


class Scraper:
    update_interval = settings.REDDIT_UPDATE_INTERVAL

    def __init__(self, identifier, config, notifiers):
        self.config = config
        self.identifier = identifier
        self.notifiers = notifiers

        logger.info('{} initialised'.format(self))

    def scrape(self):
        crawler_config = {
            'ITEM_PIPELINES': {
                'news_scraper.scraper.pipelines.twitter.TwitterPipeline': 100,
                'news_scraper.scraper.pipelines.analyse_date.AnalysePipeline': 800
            },
            'DOWNLOADER_MIDDLEWARES': {
                'news_scraper.scraper.twitter.TwitterDownloaderMiddleware': 10
            }
        }

        start_scraping(spider_config=crawler_config,
                       spiders=[(TwitterSpider, {'linked_coin': self.identifier,
                                                 'config': self.config,
                                                 'notifiers': self.notifiers})])

    def __str__(self):
        return "<TwitterScraper {}>".format(self.identifier)


if __name__ == '__main__':
    reddit = Reddit(client_id='Rm_w3TCY3erL3w',
                    client_secret='yJxgYH8AeyheshZLw0YhLHKwi9U',
                    username='jinnerbichler',
                    password='Hannes1987',
                    user_agent='testscript by /u/jinnerbichler')

    subreddit = reddit.subreddit('iota').hot(limit=30)
    for submission in subreddit:
        submission.comment_sort = 'new'
        submission.comments.replace_more(limit=0)
        print('Submission: {}'.format(submission.title))
        creation_time = datetime.utcfromtimestamp(submission.created_utc)
        for comment in submission.comments.list():
            print('  Comment: {}'.format(comment.body))
