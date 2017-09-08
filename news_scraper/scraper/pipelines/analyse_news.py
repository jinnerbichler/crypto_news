import logging

logger = logging.getLogger(__name__)


class AnalyseNewsPipeline(object):
    """Pipeline that analyses news items for certain insights"""

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_item(self, item, spider):
        return item
