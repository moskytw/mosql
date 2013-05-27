#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

conn = None

def escape(s):
    global conn
    if not conn:
        conn = MySQLdb.connect()
    return conn.escape_string(s)

import mosql.util
mosql.util.escape = escape
