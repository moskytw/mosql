#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

from mosql.result import Model

# Enable the support of MySQL-specific SQL.
import mosql.mysql

# If SQLAlchemy is installed, use its connection pool.
try:
    import sqlalchemy.pool
    MySQLdb = sqlalchemy.pool.manage(MySQLdb, pool_size=5)
except ImportError:
    pass

# If you don't use utf-8 for connection, you need to use native escape function 
# for security:
#import mosql.MySQLdb_escape
#mosql.MySQLdb_escape.conn = MySQLdb.connect(user='root', db='mosky', charset='big5')

class MySQL(Model):

    @classmethod
    def getconn(cls):

        # The ``charset='utf8'`` is just to ensure we connect db with safe
        # encoding. If
        #     ``show variables where variable_name = 'character_set_connection';``
        # shows ``utf-8``, you can ignore that.

        # The ``use_unicode=False`` is just for the consistency with another example.

        return MySQLdb.connect(user='root', db='mosky', charset='utf8', use_unicode=False)

    @classmethod
    def putconn(cls, conn):
        conn.close()
