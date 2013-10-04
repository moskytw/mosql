#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from mosql.util import raw
from mosql.query import select, left_join
from mosql.db import Database, group

db = Database(psycopg2, host='127.0.0.1')

with db as cur:

    ## Use PostgreSQL to group:

    cur.execute(select(
        'person',
        joins = left_join('detail', using='person_id'),
        where = {'key': 'email'},
        group_by = 'person_id',
        select = ('person_id', raw('array_agg(val)')),
        # It is optional here.
        order_by = 'person_id',
    ))

    print 'Group the rows in PostgreSQL:'
    for row in cur:
        print row
    print

    ## Use MoSQL (app-level) to group:

    cur.execute(select(
        'person',
        joins = left_join('detail', using='person_id'),
        where = {'key': 'email'},
        select = ('person_id', 'val'),
        # You have to order the rows!
        order_by = 'person_id',
    ))

    print 'Group the rows by MoSQL:'
    for row in group(['person_id'], cur):
        print row
