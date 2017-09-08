from django.db import models


class Tweet(models.Model):
    model_created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField()
    creator = models.TextField(default='')
    identifier = models.TextField(unique=True)
    linked_token = models.CharField(max_length=10)

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
    url = models.TextField()

    # noinspection PyRedundantParentheses
    class Meta:
        unique_together = (('crawler_id', 'title', 'text'))
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'

    def __str__(self):
        return '<NewsArticle {} from {}'.format(self.title, self.url)
