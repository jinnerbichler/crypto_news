import slackweb


class Notifier:
    def __init__(self, identifier, config):
        self.identifier = identifier
        self.slack = slackweb.Slack(url=config['url'])

    def notify(self, title, message, url):
        attachments = [{'title': title, 'title_link': url, 'text': message}]
        self.slack.notify(attachments=attachments)

    def __str__(self):
        return '<SlackNotifier {}>'.format(self.identifier)

    def __repr__(self):
        return self.__str__()
