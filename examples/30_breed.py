#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from mosql.util import star
from mosql.query import insert
from mosql.db import Database, one_to_dict

# We breed another insert with partial arguments.
person_insert = insert.breed({'table': 'person'})

dave = {
    'person_id': 'dave',
    'name'     : 'Dave',
}

db = Database(psycopg2, host='127.0.0.1')

with db as cur:

    cur.execute(person_insert(set=dave, returning=star))
    print one_to_dict(cur)
    print

    assert 0, 'Rollback!'
