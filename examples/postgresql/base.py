#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2.pool
from mosql.result import Model

# if you want to use the native escape function
#import mosql.psycopg2_escape

# The `client_encoding`='utf-8'`` is just ensure we connect db with safe encoding.
# If ``show client_encoding;` shows ``utf-8``,
# you can ignore this.
pool = psycopg2.pool.SimpleConnectionPool(1, 5, database='mosky', client_encoding='utf-8')

class PostgreSQL(Model):

    getconn = pool.getconn
    putconn = pool.putconn

