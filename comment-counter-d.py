import argparse
import praw
import logging
import sqlite3
from praw.helpers import comment_stream

from argParseLog import addLoggingArgs, handleLoggingArgs

log = logging.getLogger(__name__)

if __name__ == '__main__':
    def_sub = 'boardgames'
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--subreddit', help='The subreddit to read.', default=def_sub)
    addLoggingArgs(ap)
    args = ap.parse_args()
    handleLoggingArgs(args)

    log.info('Connecting to reddit.')
    reddit = praw.Reddit('{} bot that counts user posts in a subreddit. v.0.1'
                         ' by /u/phil_s_stein.')
    reddit.login()
    log.info('Logged in.')

    db = sqlite3.connect('{}.db'.format(args.subreddit))
    log.info('Bot database opened/created.')

    stmt = 'SELECT name FROM sqlite_master WHERE type="table" AND name="comments"'
    q = db.execute(stmt).fetchall()
    if not q:
        log.info('Creating DB tables.')
        db.execute('CREATE table comments (cid text, username text, timestamp date)')
        db.execute('CREATE table error (count integer)')

    log.info('Reading new comments from /r/{}.'.format(args.subreddit))
    subreddit = reddit.get_subreddit(args.subreddit)
    while True:
        try:
            for comment in comment_stream(reddit, subreddit):
                log.debug('read comment {} by {}'.format(comment.id, comment.author))
                # log.debug('comment {}'.format(comment.__dict__))
                # log.debug('author {}'.format(comment.author.__dict__))
                count = db.execute('SELECT COUNT(*) FROM comments WHERE cid=?', (comment.id, )).fetchall()[0][0]
                if not count or count == 0:
                    log.info('logging comment {} by {}'.format(comment.id, comment.author.name))
                    db.execute('INSERT into comments VALUES (?, ?, ?)',
                               (comment.id, comment.author.name, comment.created_utc))
                    db.commit()
        except Exception as e:
            log.error('Caught exception: {}'.format(e))
            db.execute('UPDATE error set count = count + 1')
