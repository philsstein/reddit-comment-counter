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
    then = db.execute("SELECT datetime('now', '-{} {}')".format(args.value, args.unit)).fetchone()[0]
    rows = db.execute("SELECT cid,username,datetime(timestamp, 'unixepoch') FROM comments WHERE "
                      "datetime(timestamp, 'unixepoch') > datetime('now', '-{} {}')".format(
                          args.value, args.unit)).fetchall()

    ess = 's' if args.value > 1 else ''
    print('Found {} comments from the last {} {}{}. Comments newer than {}'.format(
        len(rows), args.value, args.unit, ess, then))
    print('Oldest comment: {}'.format(rows[0][2]))

    # there is probably an SQL way to do this much much better.
    c = Counter()
    for row in rows:
        c[row[1]] += 1

    result_count = len(rows) if not args.count else args.count
    rank = 1
    print('    Rank Count Username')
    for user, count in c.most_common(result_count):
        print('    {:3}. {:5} {}'.format(rank, str(count).center(5), user))
        rank = rank + 1
