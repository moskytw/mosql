#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque

class Database(object):
    '''It is a context manager for both connection and cursor.

    :param module: a module which conforms Python DB API 2.0

    Initialize a :class:`Database` instance:

    ::

        import psycopg2
        db = Database(psycopg2, host='127.0.0.1')

    Get a cursor to communicate with database.

    ::

        with db as cur:
            cur.execute('select 1')

    The changes will be committed after you leave the with-block, or be
    rollbacked if there is any exception. The connection and cursor will also be
    closed automatically.

    Note the connection and cursor are only opened while you are in the with-block.

    If you need multiple cursors, just say:

    ::

        with db as cur1, db as cur2:
            cur1.execute('select 1')
            cur2.execute('select 2')

    The :class:`Database` has at most one connection per instance, so the two
    cursors here share the same connection.

    It is possible to customize the creating of connection or cursor. If you
    want to customize, override the functions you need:

    ::

        db = Database()
        db.getconn = lambda: pool.getconn()
        db.putconn = lambda conn: pool.putconn(conn)
        db.getcur  = lambda conn: conn.cursor('server-side cursor')

    '''

    def __init__(self, module=None, *conn_args, **conn_kargs):

        if hasattr(module, 'connect'):
            self.getconn = lambda: module.connect(*conn_args, **conn_kargs)

        # set them None to use the default way
        self.putconn = None
        self.getcur = None

        self._conn = None
        self._cur_stack = deque()

    def __enter__(self):

        # check if we need to create connection
        if not self._cur_stack:
            self._conn = self.getconn()

        # get the cursor
        if self.getcur:
            cur = self.getcur(self._conn)
        else:
            cur = self._conn.cursor()

        # push it into stack
        self._cur_stack.append(cur)

        return cur

    def __exit__(self, exc_type, exc_val, exc_tb):

        # close the cursor
        cur = self._cur_stack.pop()
        cur.close()

        # rollback or commit
        if exc_type:
            self._conn.rollback()
        else:
            self._conn.commit()

        # close the connection if all cursors are closed
        if not self._cur_stack:

            if self.putconn:
                self.putconn(self._conn)
            else:
                self._conn.close()

def extact_col_names(cur):
    '''Extacts the column names from a cursor.

    :rtype: list
    '''
    return [desc.name for desc in cur.description]

def one_to_dict(cur, row=None):
    '''Fetch one row from a cursor and make it as a dict.

    If `row` is provided, then it uses it insteand of fetching from `cur`.

    :rtype: dict
    '''

    if row is None:
        row = cur.fetchone()

    return dict(zip(extact_col_names(cur), row))

def all_to_dicts(cur, rows=None):
    '''Fetch all rows from a cursor and make it as dicts in a list.

    If `rows` is provided, then it uses it insteand of fetching from `cur`.

    :rtype: dicts in list
    '''

    if rows is None:
        rows = cur

    col_names = extact_col_names(cur)

    return [dict(zip(col_names, row)) for row in rows]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
