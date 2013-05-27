#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2.pool
from mosql.result import Model

# You need to use native escape function, if you don't use utf-8 for connection.
#import mosql.psycopg2_escape
#mosql.psycopg2_escape.conn = psycopg2.connect(database='mosky', client_encoding='big5')

# The `client_encoding`='utf-8'`` just ensures we connect db with safe encoding.
# If ``show client_encoding;` shows ``utf-8``,
# you can ignore this.
pool = psycopg2.pool.SimpleConnectionPool(1, 5, database='mosky', client_encoding='utf-8')

class PostgreSQL(Model):

    getconn = pool.getconn
    putconn = pool.putconn

