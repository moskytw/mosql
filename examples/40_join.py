#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from pprint import pprint
from mosql.query import select, left_join
from mosql.db import Database, all_to_dicts

db = Database(psycopg2, host='127.0.0.1')

with db as cur:

    cur.execute(select(
        'person',

        {'person_id': 'mosky'},
        # It is same as using keyword argument:
        #where = {'person_id': 'mosky'},

        joins = left_join('detail', using='person_id'),
        # You can also use tuple to add multiple join statements:
        #joins = (left_join('detail', using='person_id'), )
    ))

    pprint(all_to_dicts(cur))
