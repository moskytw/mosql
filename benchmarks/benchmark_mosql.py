#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import psycopg2
from getpass import getuser
from mosql.query import select

stream = sys.stderr

def info(s, end='\n'):
    stream.write(s)
    if end: stream.write(end)

conn = None
cur = None

def setup():

    cur.execute('drop table if exists _benchmark')

    cur.execute('''
        create table
            _benchmark (
                id varchar(128) primary key,
                name varchar(128)
            )
    ''')

    cur.executemany(
        'insert into _benchmark values (%s, %s)', [
        ('mosky.liu', 'Mosky Liu'),
        ('yiyu.liu', 'Yi-Yu Liu')
    ])

    #from mosql.query import insert
    #cur.execute(insert('_benchmark', values=[
    #    ('mosky.liu', 'Mosky Liu'),
    #    ('yiyu.liu', 'Yi-Yu Liu')
    #]))

    conn.commit()

    info('* The data is created.')

def execute_select():
    cur.execute(select('_benchmark', {'id': 'mosky.liu'}))
    return cur.fetchall()

def teardown():
    cur.execute('drop table _benchmark')
    conn.commit()
    info('* The data is cleaned.')

if __name__ == '__main__':

    from timeit import timeit

    info('* The benchmark for MoSQL')

    # init
    conn = psycopg2.connect(user=getuser())
    cur = conn.cursor()
    info('* The connection is opened.')
    setup()

    # benchmark
    n = 1000
    info('* Executing the bencmark (n={}) ...'.format(n))
    info('')
    print timeit(execute_select, number=n)
    info('')
    info('* Done.')

    # clean up
    teardown()
    cur.close()
    conn.close()
    info('* The connection is closed.')
