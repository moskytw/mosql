#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from mosql.util import star
from mosql.query import insert
from mosql.db import Database, one_to_dict

dave = {
    'person_id': 'dave',
    'name'     : 'Dave',
}

db = Database(psycopg2, host='127.0.0.1')

with db as cur:

    cur.execute(insert('person', dave, returning=star))
    print one_to_dict(cur)
    print

    assert 0, 'Rollback!'
