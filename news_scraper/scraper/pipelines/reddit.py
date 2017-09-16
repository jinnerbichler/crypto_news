import logging
from datetime import datetime

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
        submission = update_submission(submission_item=item['submission'].submission,
                                       notifiers=spider.notifiers)

        # create or update comments
        result_text = [submission.title]
        result_text += update_comments(authors=item['authors'],
                                       comments=item['submission'].comments,
                                       submission=submission,
                                       notifiers=spider.notifiers)

        if len(result_text) == 1:  # only submission title
            raise DropItem('Dropping submission: %s' % item)

        return {'title': 'Reddit Submission {}'.format(submission.title),
                'text': '\n'.join(result_text),
                'author': submission.author,
                'created_at': submission.created_at,
                'url': submission.url,
                'source': submission,
                'linked_coin': spider.linked_coin}


def update_submission(submission_item, notifiers):
    try:
        created_at = datetime.utcfromtimestamp(submission_item.created_utc)
        submission = RedditSubmission(identifier=submission_item.id,
                                      title=submission_item.title,
                                      self_text=submission_item.selftext,
                                      self_text_html=submission_item.selftext_html,
                                      created_at=make_aware(created_at, utc),
                                      author=submission_item.author.name,
                                      url=submission_item.url,
                                      is_video=submission_item.is_video,
                                      up_votes=submission_item.ups,
                                      down_votes=submission_item.downs,
                                      num_comments=submission_item.num_comments)
        submission.save()
        logger.debug('Created submission: {}'.format(submission.identifier))
    except IntegrityError as e:  # already exists -> update item
        submission = RedditSubmission.objects.filter(identifier=submission_item.id)
        submission = submission.first()

        # update fields
        if submission:
            submission.up_votes = submission_item.ups
            submission.down_votes = submission_item.downs
            submission.num_comments = submission_item.num_comments

            # check if submission became hot  # ToDo: check creation time
            is_hot = is_hot_submission(submission)
            if is_hot and not submission.is_hot:
                notify_all(notifiers=notifiers,
                           title='Hot Reddit Submission detected',
                           message=submission.title,
                           url=submission.url)

                logger.info('Found new hot submission: {}'.format(submission.identifier))

            submission.is_hot = is_hot
            submission.save()

            logger.debug('Updated submission: {}'.format(submission.identifier))
        else:
            logger.error('Cannot find submission: {}'.format(submission_item.id))
    return submission


# noinspection PyUnusedLocal
def update_comments(authors, comments, submission, notifiers):
    result_text = []
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
            logger.debug('Created comment: {}'.format(comment.identifier))

            # only new comments should be forwarded
            result_text.append(comment.body)

        except IntegrityError:  # already exists -> update item
            comment = RedditComment.objects.filter(identifier=comment_item.id).first()

            # update fields
            if comment:
                comment.up_votes = comment_item.ups
                comment.down_votes = comment_item.downs
                comment.save()

                # logger.debug('Updated comment: {}'.format(comment.identifier))
            else:
                logger.error('Can not find comment: {}'.format(comment_item.id))

    return result_text


def is_hot_submission(submission):
    return submission.num_comments > 15
