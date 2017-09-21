import logging
from datetime import datetime

import datefinder
from django.db import IntegrityError
from django.utils.timezone import make_aware, utc

from news_scraper.models import DetectedEvent
from news_scraper.notifier import get_notifier
import re

logger = logging.getLogger(__name__)


class AnalysePipeline(object):
    """Pipeline that analyses news items for certain insights"""

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_item(self, item, spider):
        notifier = get_notifier(notifier_id="event_found")

        # ToDo: find keywords like 'coming soon' or 'soon'

        text = item["text"]
        for date, source in datefinder.find_dates(text=text,
                                                  source=True,
                                                  base_date=datetime.now()):  # ToDO: set proper base date

            # filter false positives
            if not is_false_positive(source) and date > datetime.now():

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

    if not date_source:
        return True

    # filter sources like "may", or "mar", but not "month"
    if "month" in date_source:
        return False
    if any(s in date_source for s in ['may', 'mar', 'mon']):
        return True

    # filter inappropriate years
    for number in re.compile(r'\d{4,}').findall(date_source):
        if int(number) > datetime.now().year + 10:
            return True

    # filter inappropriate months or days (e.g. number higher than 60)
    for number in re.compile(r'\d{2,3}').findall(date_source):
        if int(number) > 60:
            return True

    invalid_regexes = [
        r'^\d*(, at| at| T| of [a-z])',  # "330, at" or "7 T"
        r'(at |of |t |of -|by )\d*$',  # "at 2305" or "at 2305"
        r'^\d*(,|[a-z]|-|^[a-z]-)\d*$',  # "147,233" or "82t2"
        r'^(t )\d*( t)$',  # "t 20 t"
        r'^\d{2}(st|nd|rd|th)$'  # "16th"
    ]
    for regex in invalid_regexes:
        if re.search(regex, date_source):
            return True

    return False
