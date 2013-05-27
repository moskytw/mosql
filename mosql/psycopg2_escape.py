#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
