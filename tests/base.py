#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from mosql.result2 import Model

class PostgreSQL(Model):
    getconn = classmethod(lambda cls: psycopg2.connect(database='mosky'))
    putconn = classmethod(lambda cls, conn: None)
