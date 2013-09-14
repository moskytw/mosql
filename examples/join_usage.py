#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import psycopg2
from pprint import pprint
from mosql.query import select, left_join

conn = psycopg2.connect(host='127.0.0.1', database=os.environ['USER'])
cur = conn.cursor()

cur.execute(select(
    'person',
    {'person_id': 'mosky'},
    joins = left_join('detail', using='person_id'),
    # You can also use tuple to add multiple join statements.
    #joins = (left_join('detail', using='person_id'), )
))

pprint(cur.fetchall())

cur.close()
#conn.commit() # Actually we don't want to commit here.
conn.close()
