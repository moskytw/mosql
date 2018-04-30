#!/usr/bin/env python
# -*- coding: utf-8 -*-


# mt: multithreading
# mp: multiprocessing


import os
import time
import threading as t
import multiprocessing as mp
import sqlite3

import funcy as fy
# import pymysql
# import sqlalchemy.pool

import mosql.db as modb


def run_in_thread(f, *args, **kwargs):
    return t.Thread(target=f, args=args, kwargs=kwargs).start()


def run_in_process(f, *args, **kwargs):
    return mp.Process(target=f, args=args, kwargs=kwargs).start()


def get_pid_tid_pair():
    return (os.getpid(), t.get_ident())


def tear_down_and_set_up(conn_f):

    conn = conn_f()
    cur = conn.cursor()

    cur.execute('drop table if exists counters;')
    cur.execute('create table counters (count int);')
    cur.execute('insert into counters values (0);')

    conn.commit()

    cur.close()
    conn.close()


def peek(conn_f):

    conn = conn_f()
    cur = conn.cursor()

    cur.execute('select * from counters;')
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return (len(rows), rows[0][0])


def run_sql_with_std_way(conn_f, sql):

    conn = conn_f()
    cur = conn.cursor()

    cur.execute(sql)
    time.sleep(0.1)

    conn.commit()

    cur.close()
    conn.close()


def run_sql_with_db(db, sql):

    with db as cur:
        cur.execute(sql)
        time.sleep(0.1)


if __name__ == '__main__':

    print('test get_pid_tid_pair')
    print(get_pid_tid_pair())
    run_in_thread(fy.rcompose(get_pid_tid_pair, print))
    run_in_process(fy.rcompose(get_pid_tid_pair, print))
    print()

    database = '/tmp/test_mt_mp.py'
    conn_f = fy.partial(sqlite3.connect, database)
    db = modb.Database(sqlite3, database)
    inc_sql = 'update counters set count = count + 1;'

    # sqlalchemy.pool.manage(sqlite3, use_threadlocal=True)

    print('test spst')
    tear_down_and_set_up(conn_f)
    run_sql_with_std_way(conn_f, inc_sql)
    run_sql_with_std_way(conn_f, inc_sql)
    peeked_retval = peek(conn_f)
    print('rows, count:', peeked_retval)
    assert peeked_retval == (1, 2)
    print()

    print('test mp std')
    tear_down_and_set_up(conn_f)
    run_sql_with_std_way(conn_f, inc_sql)
    run_sql_with_std_way(conn_f, inc_sql)
    run_in_process(run_sql_with_std_way, conn_f, inc_sql)
    run_in_process(run_sql_with_std_way, conn_f, inc_sql)
    time.sleep(0.5)
    peeked_retval = peek(conn_f)
    print('rows, count:', peeked_retval)
    assert peeked_retval == (1, 4)
    print()

    print('test mp db')
    tear_down_and_set_up(conn_f)
    run_sql_with_std_way(conn_f, inc_sql)
    run_sql_with_std_way(conn_f, inc_sql)
    run_in_process(run_sql_with_db, db, inc_sql)
    run_in_process(run_sql_with_db, db, inc_sql)
    time.sleep(0.5)
    peeked_retval = peek(conn_f)
    print('rows, count:', peeked_retval)
    assert peeked_retval == (1, 4)
    print()

    print('test mt std')
    tear_down_and_set_up(conn_f)
    run_sql_with_std_way(conn_f, inc_sql)
    run_sql_with_std_way(conn_f, inc_sql)
    run_in_thread(run_sql_with_std_way, conn_f, inc_sql)
    run_in_thread(run_sql_with_std_way, conn_f, inc_sql)
    time.sleep(0.5)
    peeked_retval = peek(conn_f)
    print('rows, count:', peeked_retval)
    assert peeked_retval == (1, 4)
    print()

    print('test mt db')
    tear_down_and_set_up(conn_f)
    run_sql_with_std_way(conn_f, inc_sql)
    run_sql_with_std_way(conn_f, inc_sql)
    run_in_thread(run_sql_with_db, db, inc_sql)
    run_in_thread(run_sql_with_db, db, inc_sql)
    # -> sqlite3.ProgrammingError in mosql 0.11
    time.sleep(0.5)
    peeked_retval = peek(conn_f)
    print('rows, count:', peeked_retval)
    assert peeked_retval == (1, 4)
    print()
