#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

from mosql.result import Model

# The patch for MySQL, because MySQL uses non-standard syntax by default.
import mosql.mysql

try:
    import sqlalchemy.pool
    MySQLdb = sqlalchemy.pool.manage(MySQLdb, pool_size=5)
except ImportError:
    pass

# You need to use native escape function, if you don't use utf-8 for connection.
#import mosql.MySQLdb_escape
#mosql.MySQLdb_escape.conn = MySQLdb.connect(user='root', db='mosky', charset='big5')

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
