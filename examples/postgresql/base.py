#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2.pool
from mosql.result import Model

# if you want to use the native escape function
#import mosql.psycopg2_escape

pool = psycopg2.pool.SimpleConnectionPool(1, 5, database='mosky')

class PostgreSQL(Model):

    getconn = pool.getconn
    putconn = pool.putconn

