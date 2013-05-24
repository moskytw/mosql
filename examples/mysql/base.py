#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

from mosql.result import Model
import mosql.mysql # a patch for MySQL's non-standard syntax

try:
    import sqlalchemy.pool
    MySQLdb = sqlalchemy.pool.manage(MySQLdb, pool_size=5)
except ImportError:
    pass

class MySQL(Model):

    @classmethod
    def getconn(cls):
        return MySQLdb.connect(user='root', db='mosky')

    @classmethod
    def putconn(cls, conn):
        conn.close()
