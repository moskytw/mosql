#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

from mosql.result import Model

# atch for MySQL, because MySQL uses non-standard syntax by default.
import mosql.mysql

# if you want to use the native escape function
#import mosql.MySQLdb_escape

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
