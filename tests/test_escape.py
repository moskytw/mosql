#!/usr/bin/env python
# -*- coding: utf-8 -*-

# test PostgreSQL
import psycopg2 as db
from mosql.util import escape
conn = db.connect(database='mosky')

# or MySQL
#import MySQLdb as db
#from mosql.mysql import escape
#from mosql.mysql import fast_escape as escape
#conn = db.connect(user='root', db='mosky')

# -- preparation --

cur = conn.cursor()

cur.execute("select * from person where person_id='dara'")
if cur.rowcount == 0:
    cur.execute("insert into person values ('dara', 'Dara Scully')")
    conn.commit()

cur.close()

# --- end of preparation ---

# --- main ---

cur = conn.cursor()

bytes = ''.join(unichr(i) for i in range(1, 128)).encode('utf-8')
bytes += ''.join(unichr(i) for i in range(28204, 28224)).encode('utf-8')

cur.execute("update person set name='%s' where person_id='dara'" % escape(bytes))
conn.commit()

cur.execute("select name from person where person_id='dara'")

for row in cur:
    name = row[0].decode('utf-8')

    print 'Check the Incontinuity:'
    count = 0
    for i in range(1, len(name)):
        diff = ord(name[i]) - ord(name[i-1])
        if 1 < diff < 20000:
            print '%s (%s) - %s (%s)' % (name[i], ord(name[i]), name[i-1], ord(name[i-1]))
            count += 1
    print 'count:', count,

    if not count:
        print 'passed!'
    else:
        print

cur.close()

# --- end of main ---

conn.close()
