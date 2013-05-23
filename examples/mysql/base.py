#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

from mosql.result import Model
import mosql.mysql # a patch for MySQL's non-standard syntax

class MySQL(Model):

    @classmethod
    def getconn(cls):
        if not hasattr(cls, '_conn'):
            cls._conn = MySQLdb.connect(user='root', db='mosky')
        return cls._conn

    @classmethod
    def putconn(cls, conn):
        pass
