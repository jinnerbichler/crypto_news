import importlib

from django.conf import settings

notifier_cache = {}


def get_notifier(notifier_id):
    if notifier_id not in settings.NOTIFIERS:
        return None

    if notifier_id not in notifier_cache:
        notifier_config = settings.NOTIFIERS[notifier_id]
        notifier_path = 'news_scraper.notifier.{}'.format(notifier_config['type'])
        notifier_module = importlib.import_module(notifier_path)
        notifier_cache[notifier_id] = notifier_module.Notifier(identifier=notifier_id,
                                                               config=notifier_config)
    return notifier_cache[notifier_id]


def notify_all(notifiers, title, message, url):
    for notifier in notifiers:
        notifier.notify(title=title, message=message, url=url)
