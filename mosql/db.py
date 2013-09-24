#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque

class ConnContext(object):

    def __init__(self, getconn, putconn=None):

        self.getconn = getconn

        if putconn:
            self.putconn = putconn
        else:
            self.putconn = lambda conn: conn.close()

        self.stack = deque()

    def __enter__(self):

        conn = self.getconn()
        cur = conn.cursor()

        self.stack.append((conn, cur))

        return cur

    def __exit__(self, exc_type, exc_val, exc_tb):

        conn, cur = self.stack.pop()

        cur.close()

        if exc_type:
            conn.rollback()
        else:
            conn.commit()

        self.putconn(conn)

def get_col_names(cur):
    return (desc.name for desc in cur.description)

def one_to_dict(cur, row=None):

    if row is None:
        row = cur.fetchone()

    return dict(zip(get_col_names(cur), row))

def all_to_dicts(cur, rows=None):

    if rows is None:
        rows = cur

    col_names = list(get_col_names(cur))

    return [dict(zip(col_names, row)) for row in rows]

