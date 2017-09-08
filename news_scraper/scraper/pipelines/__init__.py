import logging
from scrapy import logformatter

logger = logging.getLogger(__name__)


class PoliteLogFormatter(logformatter.LogFormatter):
    """Let dropped items drop silently"""

    def dropped(self, item, exception, response, spider):
        return {
            'level': logging.NOTSET,
            'msg': logformatter.DROPPEDMSG,
            'args': {
                'exception': exception,
                'item': item,
            }
        }
