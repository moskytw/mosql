#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import psycopg2

conn = psycopg2.connect(database='mosky')
cur = conn.cursor()

cur.execute('select * from users')
pprint(cur.fetchall())

cur.execute('select user_id, array_agg(name) from users group by user_id')
pprint(cur.fetchall())

cur.execute('select * from details')
pprint(cur.fetchall())

cur.execute('select user_id, key, array_agg(detail_id), array_agg(val) from details group by user_id, key')
pprint(cur.fetchall())

cur.execute('select user_id, array_agg(key), array_agg(detail_id), array_agg(val) from details group by user_id')
pprint(cur.fetchall())

conn.close()
