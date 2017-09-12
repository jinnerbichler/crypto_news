import logging
from datetime import datetime

import datefinder
from django.conf import settings
from corenlp import CoreNLPClient

from news_scraper.notifier import get_notifier

logger = logging.getLogger(__name__)


class AnalysePipeline(object):
    """Pipeline that analyses news items for certain insights"""

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_item(self, item, spider):
        notifier = get_notifier(notifier_id='date_found')

        text = item['text']
        for date, source in datefinder.find_dates(text, source=True, base_date=datetime.now()):

            logger.info('Found date {} in {}'.format(date, item['title']))

            # filter false positives
            if not is_false_positive(source):
                if notifier:
                    notifier.notify(title='Found date in {}'.format(item['title']),
                                    message='Found {} in "{}"'.format(date, source),
                                    url=item['url'])

        # with CoreNLPClient(annotators="tokenize ssplit depparse ner".split(),
        #                    start_server=False,
        #                    endpoint=settings.CORENLP_ENDPOINT) as client:
        #     ann = client.annotate(text)

        return item


def is_false_positive(date_source):
    tokens = date_source.split()

    # filter years (e.g. 2017)
    if date_source.isdigit():
        return True

    # filter sources like "500, 4"
    if any(len(t) == 1 for t in tokens):
        return True

    # to filter:
    # "at 2305"
    # "to mar"
    # "330, at"
    # "20, at"
    # "of 54"
    # "of 147,233"
    # "16th"
    # "of 90"
    # "by mar"

    return False
