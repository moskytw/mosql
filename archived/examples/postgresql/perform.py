#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import PostgreSQL

PostgreSQL.dump_sql = True

PostgreSQL.perform(
    'INSERT INTO person VALUES (%s, %s)',
    params = [
        ('dara', 'Dara Torres'),
        ('eden', 'Eden Tseng'),
    ]
)

PostgreSQL.perform("DELETE FROM person WHERE person_id = 'dara'")
PostgreSQL.perform("DELETE FROM person WHERE person_id = %s", ('eden', ))

#print PostgreSQL.perform(proc='add', param=(1, 2)).fetchall()
