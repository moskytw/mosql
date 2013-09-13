#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mosql.psycopg2_escape
from mosql.util import escape
s = "Hello, 'World'! and slash \me"

print escape(s)

import psycopg2
mosql.psycopg2_escape.conn = psycopg2.connect(dbname='mosky')

print escape(s)


import mosql.MySQLdb_escape
from mosql.util import escape
s = "Hello, 'World\xcc'! and slash \me"

print escape(s)

import MySQLdb
mosql.MySQLdb_escape.conn = MySQLdb.connect(user='root', db='mosky', charset='big5')

print escape(s)
