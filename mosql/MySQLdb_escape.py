#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
It applies the escape function in MySQLdb to :mod:`mosql.util`.

Usage:

::

    import mosql.MySQLdb_escape
    mosql.MySQLdb_escape.conn = CONNECTION

It will replace the escape functions in :mod:`mosql.util`.

.. versionadded :: 0.3
'''

import MySQLdb

conn = None

def escape(s):
    global conn
    if not conn:
        conn = MySQLdb.connect()
    return conn.escape_string(s)

import mosql.util
mosql.util.escape = escape
