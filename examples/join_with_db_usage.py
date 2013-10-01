#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from pprint import pprint
from mosql.query import select, left_join
from mosql.db import *

db = Database(psycopg2, host='127.0.0.1')

with db as cur:

    cur.execute(select(
        'person',
        joins = left_join('detail', using='person_id'),
        order_by = 'person_id'
    ))

    groups = group(['person_id'], cur, drop_key=True, to_dict=True, to_index=True)

    pprint(groups['mosky',])

    print pluck(groups['mosky',], 'val')
