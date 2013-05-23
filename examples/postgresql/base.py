#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2.pool
from mosql.result import Model

pool = psycopg2.pool.SimpleConnectionPool(1, 5, database='mosky')

class PostgreSQL(Model):

    getconn = pool.getconn
    putconn = pool.putconn
