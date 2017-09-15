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
