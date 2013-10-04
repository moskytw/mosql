#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from mosql.util import star
from mosql.query import insert

conn = psycopg2.connect(host='127.0.0.1')
cur = conn.cursor()

dave = {
    'person_id': 'dave',
    'name'     : 'Dave',
}

# MoSQL is here! :)
cur.execute(insert('person', dave, returning=star))

person_id, name = cur.fetchone()
print person_id
print name

cur.close()
#conn.commit() # Actually we don't want to commit here.
conn.close()
