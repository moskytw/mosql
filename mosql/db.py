#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It makes using the module which conforms Python DB API 2.0 easier.

The context manager for both connection and cursor:

.. autosummary ::
    Database

The functions designed for cursor:

.. autosummary ::
    extact_col_names
    one_to_dict
    all_to_dicts
    group

'''

from itertools import groupby, izip
from collections import deque

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
    they will be closed when you leave. Also, the changes will be committed when
    you leave, or be rollbacked if there is any exception.

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
    '''

    def __init__(self, module=None, *conn_args, **conn_kargs):

        if module is not None:
            self.getconn = lambda: module.connect(*conn_args, **conn_kargs)
        else:
            self.getconn = None

        self.putconn = lambda conn: conn.close()
        self.getcur  = lambda conn: conn.cursor()
        self.putcur  = lambda cur : cur.close()

        self._conn = None
        self._cur_stack = deque()

    def __enter__(self):

        # check if we need to create connection
        if not self._cur_stack:
            assert callable(self.getconn), "You must set getconn if you don't \
                specify a module."
            self._conn = self.getconn()

        # get the cursor
        cur = self.getcur(self._conn)

        # push it into stack
        self._cur_stack.append(cur)

        return cur

    def __exit__(self, exc_type, exc_val, exc_tb):

        # close the cursor
        cur = self._cur_stack.pop()
        self.putcur(cur)

        # rollback or commit
        if exc_type:
            self._conn.rollback()
        else:
            self._conn.commit()

        # close the connection if all cursors are closed
        if not self._cur_stack:
            self.putconn(self._conn)

def extact_col_names(cur):
    '''Extracts the column names from a cursor.

    :rtype: list
    '''
    return [desc.name for desc in cur.description]

def one_to_dict(cur=None, row=None, col_names=None):
    '''Fetch one row from a cursor and make it as a dict.

    If `col_names` or `row` is provided, it will be used first.

    :rtype: dict
    '''

    if col_names is None:
        assert cur is not None, 'You must specify cur or col_names.'
        col_names = extact_col_names(cur)

    if row is None:
        assert cur is not None, 'You must specify cur or row.'
        row = cur.fetchone()

    return dict(izip(col_names, row))

def all_to_dicts(cur=None, rows=None, col_names=None):
    '''Fetch all rows from a cursor and make it as dicts in a list.

    If `col_names` and `rows` are provided, it will use them first.

    :rtype: dicts in list
    '''

    if col_names is None:
        assert cur is not None, 'You must specify cur or col_names.'
        col_names = extact_col_names(cur)

    if rows is None:
        assert cur is not None, 'You must specify cur or rows.'
        rows = cur

    return [dict(izip(col_names, row)) for row in rows]

def group(by_col_names, cur=None, rows=None, col_names=None):
    '''Group the rows in application-level.

    If `col_names` and `rows` are provided, it will use them first.

    :rtype: row generator

    The examples:

    ::

        col_names = ['id', 'email']
        rows = [
            ('alice', 'alice@gmail.com'),
            ('mosky', 'mosky@gmail.com'),
            ('mosky', 'mosky.liu@pinkoi.com')
        ]

        for row in group(['id'], rows=rows, col_names=col_names):
            print row

    Or you have a cursor instance:

    ::

        for row in group(['id'], cur):
            print row

    '''

    if col_names is None:
        assert cur is not None, 'You must specify cur or col_names.'
        col_names = extact_col_names(cur)

    if rows is None:
        assert cur is not None, 'You must specify cur or rows.'
        rows = cur

    name_index_map = {name: idx for idx, name in enumerate(col_names)}
    key_indexes = tuple(name_index_map.get(name) for name in by_col_names)
    key_func = lambda row: tuple(row[i] for i in key_indexes)

    for key_values, rows_islice in groupby(rows, key_func):
        row = [list(col) for col in izip(*rows_islice)]
        for key_index, key_value in izip(key_indexes, key_values):
            row[key_index] = key_value
        yield tuple(row)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
