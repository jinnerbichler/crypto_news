from praw import Reddit
from datetime import datetime

if __name__ == '__main__':
    reddit = Reddit(client_id='Rm_w3TCY3erL3w',
                    client_secret='yJxgYH8AeyheshZLw0YhLHKwi9U',
                    username='jinnerbichler',
                    password='Hannes1987',
                    user_agent='testscript by /u/jinnerbichler')

    subreddit = reddit.subreddit('iota').hot(limit=30)
    for submission in subreddit:
        submission.comment_sort = 'new'
        submission.comments.replace_more(limit=0)
        print('Submission: {}'.format(submission.title))
        creation_time = datetime.utcfromtimestamp(submission.created_utc)
        for comment in submission.comments.list():
            print('  Comment: {}'.format(comment.body))
