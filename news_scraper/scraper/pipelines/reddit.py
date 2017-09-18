import logging
from datetime import datetime

from django.conf import settings
from django.db import IntegrityError
from django.utils.timezone import make_aware, utc
from scrapy.exceptions import DropItem

from news_scraper.models import RedditSubmission, RedditComment
from news_scraper.notifier import notify_all

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class RedditPipeline(object):
    """Pipeline that filters, pre-processes and stores Reddit submission and comments."""

    def process_item(self, item, spider):
        # update or create submission
        submission_item = item['submission'].submission
        submission, is_new = update_submission(submission_item=submission_item,
                                               notifiers=spider.notifiers,
                                               linked_coin=spider.linked_coin)

        # create or update comments
        new_comments = update_comments(authors=item['authors'],
                                       comments=item['submission'].comments,
                                       submission=submission,
                                       notifiers=spider.notifiers)

        # create resulting text
        result_text = [submission.title] if is_new else []
        result_text += [c.body for c in new_comments]

        # check if new entries
        if len(result_text) == 0:
            raise DropItem('Dropping submission: %s' % item)

        logger.info('{} submission: {} with {} new comments'.format(
            'Created' if is_new else 'Updated',
            submission.identifier,
            len(result_text) - 1))

        return {'title': 'Reddit Submission {}'.format(submission.title),
                'text': '\n'.join(result_text),
                'author': submission.author,
                'created_at': submission.created_at,
                'url': submission.url,
                'source': submission,
                'linked_coin': spider.linked_coin}


def update_submission(submission_item, notifiers, linked_coin):
    is_new = False
    try:
        created_at = datetime.utcfromtimestamp(submission_item.created_utc)
        submission = RedditSubmission(identifier=submission_item.id,
                                      title=submission_item.title,
                                      self_text=submission_item.selftext,
                                      self_text_html=submission_item.selftext_html,
                                      created_at=make_aware(created_at, utc),
                                      author=submission_item.author.name,
                                      url=submission_item.shortlink,
                                      is_video=submission_item.is_video,
                                      up_votes=submission_item.ups,
                                      down_votes=submission_item.downs,
                                      num_comments=submission_item.num_comments)
        submission.save()
        is_new = True
        logger.debug('Created submission: {}'.format(submission.identifier))

    except IntegrityError:  # already exists -> update item
        submission = RedditSubmission.objects.filter(identifier=submission_item.id)
        submission = submission.first()

        # update fields
        if submission:
            submission.up_votes = submission_item.ups
            submission.down_votes = submission_item.downs
            submission.num_comments = submission_item.num_comments
            submission.save()
        else:
            logger.error('Cannot find submission: {}'.format(submission_item.id))

    # check if submission became hot  # ToDo: check creation time
    is_hot = is_hot_submission(submission)
    if is_hot and not submission.is_hot:  # check change
        notify_all(notifiers=notifiers,
                   title='Hot Reddit Submission detected for {}'.format(linked_coin),
                   message=submission.title,
                   url=submission.url)
        logger.info('Found new hot submission: {}'.format(submission.identifier))

        # store hotness :)
        submission.is_hot = is_hot
        submission.save()

    return submission, is_new


# noinspection PyUnusedLocal
def update_comments(authors, comments, submission, notifiers):
    new_comments = []
    for comment_item in comments:
        try:

            # ToDo: filter iotabot comments

            created_at = datetime.utcfromtimestamp(comment_item.created_utc)
            author = authors[comment_item.id]
            comment = RedditComment(identifier=comment_item.id,
                                    created_at=make_aware(created_at, utc),
                                    author=author.name if author else 'None',
                                    body=comment_item.body,
                                    body_html=comment_item.body_html,
                                    up_votes=comment_item.ups,
                                    down_votes=comment_item.downs,
                                    parent_submission=submission)
            comment.save()

            # only new comments should be forwarded
            new_comments.append(comment)

        except IntegrityError:  # already exists -> update item
            comment = RedditComment.objects.filter(identifier=comment_item.id).first()

            # update fields
            if comment:
                comment.up_votes = comment_item.ups
                comment.down_votes = comment_item.downs
                comment.save()
            else:
                logger.error('Can not find comment: {}'.format(comment_item.id))

    return new_comments


def is_hot_submission(submission):
    return submission.num_comments > settings.REDDIT_HOT_THRESHHOLD
