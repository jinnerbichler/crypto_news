import logging
from datetime import datetime

import datefinder
from django.db import IntegrityError
from django.utils.timezone import make_aware, utc

from news_scraper.models import DetectedEvent
from news_scraper.notifier import get_notifier

logger = logging.getLogger(__name__)


class AnalysePipeline(object):
    """Pipeline that analyses news items for certain insights"""

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_item(self, item, spider):
        notifier = get_notifier(notifier_id="date_found")

        # ToDo: find keywords like 'coming soon' or 'soon'

        text = item["text"]
        for date, source in datefinder.find_dates(text, source=True,
                                                  base_date=datetime.now()):  # ToDO: set proper base date

            # filter false positives
            if not is_false_positive(source):

                try:
                    event = DetectedEvent(date=make_aware(date, utc),
                                          name="Found date in {}".format(item["title"]),
                                          url=item['url'],
                                          text_source=source)
                    event.save()

                    logger.info("Found new date {} in {}".format(date, item["title"]))

                    if notifier:
                        notifier.notify(title=event.name,
                                        message='Found {} in "{}"'.format(date, source),
                                        url=item["url"])
                except IntegrityError:
                    pass

        # with CoreNLPClient(annotators="tokenize ssplit depparse ner".split(),
        #                    start_server=False,
        #                    endpoint=settings.CORENLP_ENDPOINT) as client:
        #     ann = client.annotate(text)

        return item


def is_false_positive(date_source):
    if date_source is None or len(date_source) == 0:
        return True

    tokens = date_source.split()

    # filter years (e.g. 2017)
    if date_source.isdigit():
        return True

    # filter sources like "16th"
    if len(tokens) == 1 and any(date_source.endswith(e) for e in ["st", "nd", "rd", "th"]):
        return True

    # filter tokens like "330, at" or "20, at"
    if tokens[0].endswith(',') and not tokens[-1].isdigit():
        return True

    # filter sources like "at 2305" or "at 2305"
    if len(tokens) == 2 and len(tokens[0]) == 2 and tokens[-1].isdigit():
        return True

    # filter sources like "by mar" or "to mar"
    if len(tokens) == 2 and len(tokens[0]) == 2 and not tokens[0].isdigit() \
            and all(not c.isdigit() and c.islower() for c in tokens[-1]):
        return True

    # filter sources like "of 147,233"
    if len(tokens) == 2 and len(tokens[0]) == 2 and all(s.isdigit() for s in tokens[-1].split(",")):
        return True

    # filter sources like "may"
    if "may" in date_source:
        return True

    # filter tokes like "on to mon" or "of 155 sat"
    if len(tokens[-1]) == 3 and all(not c.isdigit() and c.islower() for c in tokens[-1]):
        return True

    # filter sources like "500, 4"
    if len(tokens[-1]) == 1 and tokens[-1].isdigit():
        return True

    # filter tokes like "t 2017" or "t 12"
    if len(tokens) == 2 and len(tokens[0]) == 1 and tokens[0].isalpha() and tokens[-1].isdigit():
        return True

    # filter tokes like "7 T"
    if len(tokens) == 2 and tokens[0].isdigit() and tokens[-1].isalpha() and len(tokens[-1]) == 1:
        return True

    for token in tokens:
        # filter sources like "f" or "4,327"
        if ',' in token and any(st.isdigit() for st in token.split(",")):
            return True

        # filter three digit letters
        if len(token) == 3 and token.isdigit():
            return True

        # filter tokens like "08t2", "2t" or "33d"
        num_digits = len([c for c in token if c.isdigit()])
        num_letters = len([c for c in token if c.isalpha()])
        if num_letters == 1 and num_digits > 0:
            return True

    return False
