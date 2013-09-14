#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import psycopg2
from mosql.util import star
from mosql.query import insert, select, update, delete

conn = psycopg2.connect(host='127.0.0.1', database=os.environ['USER'])
cur = conn.cursor()

# We breed another insert with parital arguments.
person_insert = insert.breed({'table': 'person'})

dave = {
    'person_id': 'dave',
    'name'     : 'Dave',
}

cur.execute(person_insert(set=dave, returning=star))

person_id, name = cur.fetchone()
print person_id
print name

cur.close()
#conn.commit() # Actually we don't want to commit here.
conn.close()
