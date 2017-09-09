import logging
from django.conf import settings
from corenlp import CoreNLPClient

logger = logging.getLogger(__name__)


class AnalyseNewsPipeline(object):
    """Pipeline that analyses news items for certain insights"""

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_item(self, item, spider):
        text = item['text']

        with CoreNLPClient(annotators="tokenize ssplit depparse ner".split(),
                           start_server=False,
                           endpoint=settings.CORENLP_ENDPOINT) as client:
            ann = client.annotate(text)

        return item
