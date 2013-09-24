#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque

class Database(object):

    def __init__(self, module, *conn_args, **conn_kargs):

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

def get_col_names(cur):
    return [desc.name for desc in cur.description]

def one_to_dict(cur, row=None):

    if row is None:
        row = cur.fetchone()

    return dict(zip(get_col_names(cur), row))

def all_to_dicts(cur, rows=None):

    if rows is None:
        rows = cur

    col_names = get_col_names(cur)

    return [dict(zip(col_names, row)) for row in rows]

