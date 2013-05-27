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
        # The ``charset='utf8'`` is just ensure we connect db with safe encoding
        # If ``show variables where variable_name = 'character_set_connection';`` shows ``utf-8``,
        # you can ignore this.
        # The ``use_unicode=False`` is just for the consistency with another example.
        return MySQLdb.connect(user='root', db='mosky', charset='utf8', use_unicode=False)

    @classmethod
    def putconn(cls, conn):
        conn.close()
