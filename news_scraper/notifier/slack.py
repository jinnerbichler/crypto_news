from slackclient import SlackClient
from django.conf import settings

slack_client = SlackClient(settings.SLACK_TOKEN)


class Notifier:
    def __init__(self, identifier, config):
        self.identifier = identifier
        self.channel = config['channel']

    def notify(self, title, message, url=None):
        attachments = [{'title': title, 'title_link': url, 'text': message}]
        response = slack_client.api_call('chat.postMessage',
                                         channel=self.channel,
                                         attachments=attachments)
        if not response['ok']:
            raise AttributeError(str(response))

    def __str__(self):
        return '<SlackNotifier {}/{}>'.format(self.identifier, self.channel)

    def __repr__(self):
        return self.__str__()
