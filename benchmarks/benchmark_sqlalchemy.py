#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from getpass import getuser
from sqlalchemy.sql import select
from sqlalchemy import create_engine, MetaData, Table, Column, String

stream = sys.stderr

def info(s, end='\n'):
    stream.write(s)
    if end: stream.write(end)

metadata = MetaData()
benchmark = Table('_benchmark', metadata,
    Column('id', String(128), primary_key=True),
    Column('name', String(128)),
)

engine = None
conn = None

def setup():

    conn.execute('drop table if exists _benchmark')

    conn.execute('''
        create table
            _benchmark (
                id varchar(128) primary key,
                name varchar(128)
            )
    ''')

    conn.execute(benchmark.insert().values([
        {'id': 'mosky.liu', 'name': 'Mosky Liu'},
        {'id': 'yiyu.liu', 'name': 'Yi-Yu Liu'}
    ]))

    info('* The data is created.')

def execute_select():
    return conn.execute(
        benchmark.select().where(benchmark.c.id == 'mosky.liu')
    ).fetchall()

def teardown():
    conn.execute('drop table _benchmark')
    info('* The data is cleaned.')

if __name__ == '__main__':

    from timeit import timeit

    info('* The benchmark for SQLAlchemy')

    # init
    # It seems SQLAlchemy is hard to co-work with native Psycopg2, so we use the
    # its engine.
    user_name = getuser()
    engine = create_engine('postgresql://{}@localhost/{}'.format(user_name, user_name))
    conn = engine.connect() # autocommit
    info('* The connection is opened.')
    setup()

    n = 1000
    info('* Executing the bencmark (n={}) ...'.format(n))
    info('')
    print timeit(execute_select, number=n)
    info('')
    info('* Done.')

    # clean up
    teardown()
    conn.close()
    info('* The connection is closed.')
