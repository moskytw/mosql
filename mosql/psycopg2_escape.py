#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
.. deprecated:: 0.6
    You should use safe connection encoding, such as utf-8. This module will be
    removed in a future release.

It applies the escape function in psycopg2 to :mod:`mosql.util`.

Usage:

::

    import mosql.psycopg2_escape
    mosql.psycopg2_escape.conn = CONNECTION

It will replace the escape functions in :mod:`mosql.util`.

.. versionadded :: 0.3
'''

from psycopg2.extensions import QuotedString
import psycopg2

conn = None

def escape(s):
    qs = QuotedString(s)
    if conn:
        qs.prepare(conn)
    return qs.getquoted()[1:-1]

import mosql.util
mosql.util.escape = escape
