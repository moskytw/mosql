#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It makes it easier to use the module which conforms Python DB API 2.0.

The context manager for both connection and cursor:

.. autosummary::
    Database

The functions designed for cursor:

.. autosummary::
    extract_col_names
    one_to_dict
    all_to_dicts
    group

'''


import os
import threading
from itertools import groupby
from collections import deque, defaultdict

from .compat import PY2, izip


if PY2:
    def _get_pid_tid_pair():
        return (os.getpid(), threading.current_thread().ident)
else:
    def _get_pid_tid_pair():
        return (os.getpid(), threading.get_ident())


class Database(object):
    '''It is a context manager which manages the creation and destruction of a
    connection and its cursors.

    :param module: a module which conforms Python DB API 2.0

    Initialize a :class:`Database` instance:

    ::

        import psycopg2
        db = Database(psycopg2, host='127.0.0.1')

    Note it just tells :class:`Database` how to connect to your database. No
    connection or cursor is created here.

    Then get a cursor to communicate with database:

    ::

        with db as cur:
            cur.execute('select 1')

    The connection and cursor are created when you enter the with-block, and
    they will be closed when you leave. Also, the changes will be committed at
    the same time, or be rollbacked if there is any exception.

    If you need multiple cursors, just say:

    ::

        with db as cur1, db as cur2:
            cur1.execute('select 1')
            cur2.execute('select 2')

    Each :class:`Database` instance at most has one connection. The cursors
    share a same connection no matter how many cursors you asked.

    It is possible to customize the creating of connection or cursor. If you
    want to customize, override the attributes you need:

    ::

        db = Database()
        db.getconn = lambda: pool.getconn()
        db.putconn = lambda conn: pool.putconn(conn)
        db.getcur  = lambda conn: conn.cursor('named-cusor')
        db.putcur  = lambda cur : cur.close()

    By default, the connection will be closed when you leave with-block. If you
    want to keep the connection open, set `to_keep_conn` as ``True``. It will
    be useful in single threading environment.

    ::

        db.to_keep_conn = True

    .. versionadded:: 0.10
        the `to_keep_conn`.

    .. versionchanged:: 0.10
        This class is thread-safe now.

    .. versionchanged:: 0.12
        This class supports multithreading and multiprocessing better now.

    .. versionchanged:: 0.12.3
        When the nest with case, it only commits after exit the first with.

    '''

    def __init__(self, module=None, *conn_args, **conn_kargs):

        self.getconn = lambda: module.connect(*conn_args, **conn_kargs)
        self.putconn = lambda conn: conn.close()
        self.getcur  = lambda conn: conn.cursor()
        self.putcur  = lambda cur : cur.close()

        self.to_keep_conn = False

        # consider multithreading and multiprocessing environment
        # built-in thread local doesn't have the default feature
        self._thread_local = defaultdict(lambda: {
            'conn': None,
            'cur_stack': deque()
        })

    def __enter__(self):

        tl = self._thread_local[_get_pid_tid_pair()]
        conn = tl['conn']
        cur_stack = tl['cur_stack']

        # conn won't be cleared if nested with or to_keep_conn is True
        if conn is None:
            conn = tl['conn'] = self.getconn()

        cur = self.getcur(conn)
        cur_stack.append(cur)

        return cur

    def __exit__(self, exc_type, exc_val, exc_tb):

        tl = self._thread_local[_get_pid_tid_pair()]
        conn = tl['conn']
        cur_stack = tl['cur_stack']

        cur = cur_stack.pop()
        self.putcur(cur)

        if exc_type:
            conn.rollback()
        # only commit when the exit of the first with
        elif not cur_stack:
            conn.commit()

        if not cur_stack and not self.to_keep_conn:
            self.putconn(conn)
            conn = tl['conn'] = None


def extract_col_names(cur):
    '''Extracts the column names from a cursor.

    :rtype: list
    '''
    return [desc[0] for desc in cur.description]


def one_to_dict(cur=None, row=None, col_names=None):
    '''Fetch one row from a cursor and make it as a dict.

    If `col_names` or `row` is provided, it will be used first.

    :rtype: dict
    '''

    if col_names is None:
        assert cur is not None, 'You must specify cur or col_names.'
        col_names = extract_col_names(cur)

    if row is None:
        assert cur is not None, 'You must specify cur or row.'
        row = cur.fetchone()

    return dict(izip(col_names, row))


def all_to_dicts(cur=None, rows=None, col_names=None):
    '''Fetch all rows from a cursor and make them as dicts in a list.

    If `col_names` or `rows` is provided, it will be used first.

    :rtype: dicts in list
    '''

    if col_names is None:
        assert cur is not None, 'You must specify cur or col_names.'
        col_names = extract_col_names(cur)

    if rows is None:
        assert cur is not None, 'You must specify cur or rows.'
        rows = cur

    return [dict(izip(col_names, row)) for row in rows]


def group(by_col_names, cur=None, rows=None, col_names=None, to_dict=False):
    '''Groups the rows in application-level.

    If `col_names` or `rows` is provided, it will be used first.

    :rtype: row generator

    Assume we have a cursor named ``cur`` has the data:

    ::

        col_names = ['id', 'email']
        rows = [
            ('alice', 'alice@gmail.com'),
            ('mosky', 'mosky.tw@gmail.com'),
            ('mosky', 'mosky.liu@pinkoi.com')
        ]

    Group the rows in ``cur`` by id.

    ::

        for row in group(['id'], cur):
            print row

    The output:

    ::

        ('alice', ['alice@gmail.com'])
        ('mosky', ['mosky.tw@gmail.com', 'mosky.liu@pinkoi.com'])

    '''

    if col_names is None:
        assert cur is not None, 'You must specify cur or col_names.'
        col_names = extract_col_names(cur)

    if rows is None:
        assert cur is not None, 'You must specify cur or rows.'
        rows = cur

    name_index_map = dict((name, idx) for idx, name in enumerate(col_names))
    key_indexes = tuple(name_index_map.get(name) for name in by_col_names)
    key_func = lambda row: tuple(row[i] for i in key_indexes)

    for key_values, rows_islice in groupby(rows, key_func):

        # TODO: the performance

        row = [list(col) for col in izip(*rows_islice)]
        for key_index, key_value in izip(key_indexes, key_values):
            row[key_index] = key_value

        if to_dict:
            yield one_to_dict(row=row, col_names=col_names)
        else:
            yield tuple(row)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
