import argparse
import logging
import sqlite3
from collections import Counter

from argParseLog import addLoggingArgs, handleLoggingArgs

log = logging.getLogger(__name__)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--database', help='The database to read.', default='boardgames.db')
    ap.add_argument('-u', '--unit', help='List post count by time ago given.',
                    choices=['second', 'minute', 'hour', 'day', 'week', 'month', 'year'])
    ap.add_argument('-v', '--value', help='How many of the unit to have. i.e. -v 1 -u \'day\''
                    ' is one day ago.', type=int)
    ap.add_argument('-c', '--count', help='Number of results to return.', type=int)
    addLoggingArgs(ap)
    args = ap.parse_args()
    handleLoggingArgs(args)

    db = sqlite3.connect(args.database)

    # select count(*) from comments where datetime(timestamp, 'unixepoch') > datetime('now', '-1 hour');
    rows = db.execute("SELECT * FROM comments WHERE datetime(timestamp, 'unixepoch') > "
                      "datetime('now', '-{} {}')".format(args.value, args.unit)).fetchall()

    ess = 's' if args.value > 1 else ''
    print('Found {} comments from the last {} {}{}.'.format(len(rows), args.value, args.unit, ess))

    # there is probably an SQL way to do this much much better.
    c = Counter()
    for row in rows:
        c[row[1]] += 1

    result_count = len(rows) if not args.count else args.count
    for user, count in c.most_common(result_count):
        print('{:4} - {}'.format(count, user))
