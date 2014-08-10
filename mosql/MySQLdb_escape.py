#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
.. deprecated:: 0.6
    You should use safe connection encoding, such as utf-8. This module will be
    removed in a future release.

It applies the escape function in MySQLdb to :mod:`mosql.util`.

Usage:

::

    import mosql.MySQLdb_escape
    mosql.MySQLdb_escape.conn = CONNECTION

It will replace the escape functions in :mod:`mosql.util`.

.. versionadded :: 0.3
'''

# --- the removal warning ---
from .util import print_warning
print_warning('mosql.MySQL_escape will be removed at version 1.0.')
# --- end ---

import MySQLdb

conn = None

def escape(s):
    global conn
    if not conn:
        conn = MySQLdb.connect()
    return conn.escape_string(s)

import mosql.util
mosql.util.escape = escape
