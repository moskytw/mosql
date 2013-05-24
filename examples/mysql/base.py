#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

from mosql.result import Model

# Patch for MySQL, because MySQL uses non-standard syntax by default.
import mosql.mysql

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
