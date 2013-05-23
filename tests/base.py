#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from mosql.result2 import Model

class PostgreSQL(Model):

    @staticmethod
    def getconn():
        return psycopg2.connect(database='mosky')

    @staticmethod
    def putconn(conn):
        pass
