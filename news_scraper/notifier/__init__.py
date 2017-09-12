import importlib

from django.conf import settings


def get_notifier(notifier_id):
    # ToDO: create cash of notifiers

    if notifier_id not in settings.NOTIFIERS:
        return None

    notifier_config = settings.NOTIFIERS[notifier_id]
    notifier_path = 'news_scraper.notifier.{}'.format(notifier_config['type'])
    notifier_module = importlib.import_module(notifier_path)
    return notifier_module.Notifier(identifier=notifier_id, config=notifier_config)
