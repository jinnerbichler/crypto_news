# CryptoNewsBot

## Configuration

The central configuration is stored in `./crypto_news/settings.py` and consists of two main fields (i.e. `NOTIFIERS` and `SCRAPERS`).

### Notifiers

Currently only Slack notifiers are supported.

The following snippets defines a Slack notifier, whereas the webhook url is stored in the environment variable `IOTA_SLACK_WEBHOOK_URL`.

```
NOTIFIERS = {
    'iota_slack': {
        'type': 'slack',
        'url': os.getenv('IOTA_SLACK_WEBHOOK_URL')
    }
}
```

### Scrapers

Currently only Twitter scrapers are supported.
The following snippet scrapes IOTA related tweets, which are releated to the defined set of users or include at least one of the defined hashtags. It is possible to exclude certain tweets from specific users. Scraped tweets are distributed via defined notifiers (e.g. `iota_slack`).

```
SCRAPERS = {
    'IOTA': {
        'scrapers': {
            'twitter': {
                'users': ['@iotatoken', '@tangleblog', '@DomSchiener ', '@DavidSonstebo'],
                'hashtags': ['#iotatoken', '#iota'],
                'exclude_users': ['@coinstats', '@analysisinchain',
                                  '@iota_market', '@dx_alert']
            }
        },
        'notifiers': ['iota_slack']
    }
}
```

In order to access tweets from Twitter the following environment variables must be set:

* TWITTER\_API\_KEY
* TWITTER\_API\_SECRET
* TWITTER\_ACCESS\_TOKEN
* TWITTER\_ACCESS\_TOKEN\_SECRET
