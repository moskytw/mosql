#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

from mosql.result import Model
import mosql.mysql # a patch for MySQL's non-standard syntax

class MySQL(Model):

    @staticmethod
    def getconn():
        return MySQLdb.connect(user='root', db='mosky')

    @staticmethod
    def putconn(conn):
        pass
