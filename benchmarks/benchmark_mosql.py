#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
stream = sys.stderr
def info(s, end='\n'):
    stream.write(s)
    if end: stream.write(end)
info("* It benchmarks MoSQL.")

import psycopg2
from getpass import getuser
from mosql.query import select

conn = psycopg2.connect(user=getuser())
cur = conn.cursor()
info('* The connection is opened.')

def setup():

    cur.execute('drop table if exists testee')

    cur.execute('''
        create table
            testee (
                id varchar(128) primary key,
                name varchar(128)
            )
    ''')

    cur.executemany(
        'insert into testee values (%s, %s)', [
        ('mosky.liu', 'Mosky Liu'),
        ('yiyu.liu', 'Yi-Yu Liu')
    ])

    info('* The data is created.')

def execute_select():
    cur.execute(select('testee', {'id': 'mosky.liu'}))
    return cur.fetchall()

def teardown():
    cur.execute('drop table testee')
    info('* The data is cleaned.')

if __name__ == '__main__':

    from timeit import timeit

    # init
    setup()

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
