#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2.pool
from mosql.result import Model

pool = psycopg2.pool.SimpleConnectionPool(1, 100, database='mosky')

class PostgreSQL(Model):
    getconn = pool.getconn
    putconn = pool.putconn

class Person(PostgreSQL):
    table = 'person'

def use_pure_sql():
    conn = pool.getconn()
    cur = conn.cursor()

    cur.execute("select * from person where person_id in ('mosky', 'andy') order by person_id")
    result = cur.fetchall()

    cur.close()
    pool.putconn(conn)

    return result

def use_mosql():
    return Person.select(
        where    = {'person_id': ('mosky', 'andy')},
        order_by = ('person_id',)
    )

if __name__ == '__main__':

    from timeit import timeit

    #print use_pure_sql()
    #print use_mosql()
    #print use_mosql()
    print timeit(use_pure_sql, number=100000)
    # -> 35.7427990437
    print timeit(use_mosql, number=100000)
    # -> 46.7011768818
