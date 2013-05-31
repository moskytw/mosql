#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2.pool
from mosql.result import Model

# If you don't use utf-8 for connection, you need to use native escape function 
# for security:
#import mosql.psycopg2_escape
#mosql.psycopg2_escape.conn = psycopg2.connect(database='mosky', client_encoding='big5')

# The `client_encoding`='utf-8'`` is just to ensure we connect db with safe
# encoding. If ``show client_encoding;` shows ``utf-8``, you can ignore that.
pool = psycopg2.pool.SimpleConnectionPool(1, 5, database='mosky', client_encoding='utf-8')

class PostgreSQL(Model):

    getconn = pool.getconn
    putconn = pool.putconn

