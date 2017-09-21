from multiselectfield import MultiSelectField
from django.contrib.contenttypes.models import ContentType
from django.db import models

COINS = (('none', 'None'),
         ('iota', 'Iota'),
         ('etc', 'Ethereum Classic'),
         ('eth', 'Ethereum'),
         ('btc', 'Bitcoin'),
         ('dash', 'Dash'),
         ('bth', 'Bitcoin Cash'),
         ('xrp', 'Ripple'),
         ('nem', 'NEM'),
         ('xmr', 'Monero'),
         ('omg', 'OmiseGO'),
         ('neo', 'NEO'),
         ('ltc', 'Litecoin'))


class Tweet(models.Model):
    model_created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField()
    creator = models.TextField(default='')
    identifier = models.TextField(unique=True)
    linked_token = models.CharField(max_length=10)
    text = models.TextField(default='')
    is_hot = models.BooleanField(default=False)

    # noinspection PyRedundantParentheses
    class Meta:
        unique_together = (('identifier', 'linked_token'))
        verbose_name = 'Twitter Tweet'
        verbose_name_plural = 'Twitter Tweets'

    def __str__(self):
        return '<Tweet {} for token {}'.format(self.identifier, self.linked_token)


class NewsArticle(models.Model):
    model_created_at = models.DateTimeField(auto_now_add=True)
    creator_url = models.TextField()
    crawler_id = models.TextField()
    title = models.TextField()
    author = models.TextField()
    text = models.TextField()
    url = models.URLField()

    # noinspection PyRedundantParentheses
    class Meta:
        unique_together = (('crawler_id', 'title', 'url'))
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'

    def __str__(self):
        return '<NewsArticle {} from {}>'.format(self.title, self.url)


class RedditSubmission(models.Model):
    model_created_at = models.DateTimeField(auto_now_add=True)
    identifier = models.TextField()
    title = models.TextField()
    self_text = models.TextField(max_length=1024*4)
    self_text_html = models.TextField(max_length=1024*4, null=True, blank=True)
    created_at = models.DateTimeField()  # utc
    author = models.TextField()
    url = models.URLField()
    is_video = models.BooleanField(default=False)
    up_votes = models.IntegerField(default=0)
    down_votes = models.IntegerField(default=0)
    num_comments = models.IntegerField()
    is_hot = models.BooleanField(default=False)

    # noinspection PyRedundantParentheses
    class Meta:
        unique_together = (('identifier',))
        verbose_name = 'Reddit Submission'
        verbose_name_plural = 'Reddit Submissions'


class RedditComment(models.Model):
    model_created_at = models.DateTimeField(auto_now_add=True)
    identifier = models.TextField()
    created_at = models.DateTimeField()  # utc
    author = models.TextField()
    body = models.TextField(max_length=1024*4)
    body_html = models.TextField(max_length=1024*4)
    up_votes = models.IntegerField(default=0)
    down_votes = models.IntegerField(default=0)
    parent_submission = models.ForeignKey(RedditSubmission, on_delete=models.CASCADE)

    # noinspection PyRedundantParentheses
    class Meta:
        unique_together = (('identifier',))
        verbose_name = 'Reddit Comment'
        verbose_name_plural = 'Reddit Comments'


class DetectedEvent(models.Model):
    model_created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField()
    name = models.TextField()
    url = models.URLField()
    text_source = models.TextField(default='None')
    relevant_coins = MultiSelectField(choices=COINS, default=COINS[0])
    validated = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return '{} on {}'.format(self.name, self.date)
