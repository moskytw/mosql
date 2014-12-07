#!/usr/bin/env python
# -*- coding: utf-8 -*-

from getpass import getuser
from itertools import product
import mosql.util
import mosql.std
import mosql.mysql

def connect_to_postgresql():

    import psycopg2
    conn = psycopg2.connect(user=getuser())

    cur = conn.cursor()

    cur.execute('show server_encoding')
    server_encoding, = cur.fetchone()
    assert server_encoding == 'UTF8'

    cur.execute('show client_encoding')
    client_encoding, = cur.fetchone()
    assert client_encoding == 'UTF8'

    cur.close()

    return conn

def test_value_in_postgresql():

    mosql.std.patch()

    conn = connect_to_postgresql()
    cur = conn.cursor()

    cur.execute('''
        create temporary table _test_value_in_postgresql (
            k varchar(128) primary key,
            v text
        )
    ''')

    # Test V-P-1: Value - PostgreSQL - All BMP Chars
    #
    # It will include all BMP chars, except
    #
    # 1. the null byte (U+0000)
    # 2. utf-16 surrogates (U+D800-U+DBFF, U+DC00-U+DFFF)
    #
    # which are not valid string constant in PostgreSQL.
    #
    # ref: http://www.postgresql.org/docs/9.3/static/sql-syntax-lexical.html#SQL-SYNTAX-STRINGS-ESCAPE

    expected_text = u''.join(unichr(i) for i in xrange(0x0001, 0xd800))
    expected_text += u''.join(unichr(i) for i in xrange(0xe000, 0xffff+1))

    # Test V-P-1-1: Value - PostgreSQL - All BMP Chars - Raw SQL

    cur.execute('''
        insert into
            _test_value_in_postgresql
        values (
            'raw-sql-bmp',
            %s
        )
    ''', (expected_text, ))

    cur.execute('''select v from _test_value_in_postgresql where k = 'raw-sql-bmp' ''')
    fetched_bytes, = cur.fetchone()
    fetched_text = fetched_bytes.decode('utf-8')

    assert fetched_text == expected_text

    # Test V-P-1-2: Value - PostgreSQL - All BMP Chars - MoSQL's Value Function

    cur.execute('''
        insert into
            _test_value_in_postgresql
        values (
            'mosql-bmp',
            {}
        )
    '''.format(mosql.util.value(expected_text)))

    cur.execute('''select v from _test_value_in_postgresql where k = 'mosql-bmp' ''')
    fetched_bytes, = cur.fetchone()
    fetched_text = fetched_bytes.decode('utf-8')

    assert fetched_text == expected_text

    # Test V-P-2: Value - PostgreSQL - The Double ASCII Char's Dot Product
    #
    # It will include '\' + any ASCII char, and "'" + any ASCII char.
    #
    # dot product: dot_product(XY, AB) -> XAXBYAYB

    ascii_chars = [unichr(i) for i in xrange(0x01, 0x7f+1)]
    expected_text = u''.join(a+b for a, b in product(ascii_chars, ascii_chars))

    # Test V-P-2-1: Value - PostgreSQL - The Double ASCII Char's Dot Product - Raw SQL

    cur.execute('''
        insert into
            _test_value_in_postgresql
        values (
            'raw-sql-2-ascii',
            %s
        )
    ''', (expected_text, ))

    cur.execute('''select v from _test_value_in_postgresql where k = 'raw-sql-2-ascii' ''')
    fetched_bytes, = cur.fetchone()
    fetched_text = fetched_bytes.decode('utf-8')

    assert fetched_text == expected_text

    # Test V-P-2-2: Value - PostgreSQL - The Double ASCII Char's Dot Product - MoSQL's Value Function

    cur.execute('''
        insert into
            _test_value_in_postgresql
        values (
            'mosql-2-ascii',
            {}
        )
    '''.format(mosql.util.value(expected_text)))

    cur.execute('''select v from _test_value_in_postgresql where k = 'mosql-2-ascii' ''')
    fetched_bytes, = cur.fetchone()
    fetched_text = fetched_bytes.decode('utf-8')

    assert fetched_text == expected_text

    cur.close()
    conn.close()

def connect_to_mysql():

    import MySQLdb
    conn = MySQLdb.connect(user='root', db='root')

    cur = conn.cursor()

    # the columns: variable_name, value
    cur.execute('''show variables where variable_name = 'character_set_database' ''')
    _, character_set_database = cur.fetchone()
    assert character_set_database == 'utf8'

    cur.execute('''show variables where variable_name = 'character_set_connection' ''')
    _, character_set_connection = cur.fetchone()
    assert character_set_connection == 'utf8'

    cur.close()

    return conn

def test_value_in_mysql():

    mosql.mysql.patch()

    conn = connect_to_mysql()
    cur = conn.cursor()

    cur.execute('''
        create temporary table _test_value_in_mysql (
            k varchar(128) primary key,
            v mediumtext
        )
    ''')

    # Test V-M-1: Value - MySQL - All BMP Chars
    #
    # It will include all BMP chars, except
    #
    # 1. the utf-16 low surrogates (U+DC00-U+DFFF)
    #
    # which are not valid string in MySQL.
    #
    # ref: http://dev.mysql.com/doc/refman/5.7/en/string-literals.html

    expected_text = u''.join(unichr(i) for i in xrange(0x0000, 0xdc00))
    expected_text += u''.join(unichr(i) for i in xrange(0xe000, 0xffff+1))

    # Test V-M-1-1: Value - MySQL - All BMP Chars - Raw SQL

    cur.execute('''
        insert into
            _test_value_in_mysql
        values (
            'raw-sql-bmp',
            %s
        )
    ''', (expected_text, ))

    cur.execute('''select v from _test_value_in_mysql where k = 'raw-sql-bmp' ''')
    fetched_bytes, = cur.fetchone()
    fetched_text = fetched_bytes.decode('utf-8')

    assert fetched_text == expected_text

    # Test V-M-1-2: Value - MySQL - All BMP Chars - MoSQL's Value Function

    cur.execute('''
        insert into
            _test_value_in_mysql
        values (
            'mosql-bmp',
            {}
        )
    '''.format(mosql.util.value(expected_text)))

    cur.execute('''select v from _test_value_in_mysql where k = 'mosql-bmp' ''')
    fetched_bytes, = cur.fetchone()
    fetched_text = fetched_bytes.decode('utf-8')

    assert fetched_text == expected_text

    # Test V-M-2: Value - MySQL - The Double ASCII Char's Dot Product
    #
    # It will include '\' + any ASCII char, and "'" + any ASCII char.
    #
    # dot product: dot_product(XY, AB) -> XAXBYAYB

    ascii_chars = [unichr(i) for i in xrange(0x01, 0x7f+1)]
    expected_text = u''.join(a+b for a, b in product(ascii_chars, ascii_chars))

    # Test V-M-2-1: Value - MySQL - The Double ASCII Char's Dot Product - Raw SQL

    cur.execute('''
        insert into
            _test_value_in_mysql
        values (
            'raw-sql-2-ascii',
            %s
        )
    ''', (expected_text, ))

    cur.execute('''select v from _test_value_in_mysql where k = 'raw-sql-2-ascii' ''')
    fetched_bytes, = cur.fetchone()
    fetched_text = fetched_bytes.decode('utf-8')

    assert fetched_text == expected_text

    # Test V-M-2-2: Value - MySQL - The Double ASCII Char's Dot Product - MoSQL's Value Function

    cur.execute('''
        insert into
            _test_value_in_mysql
        values (
            'mosql-2-ascii',
            {}
        )
    '''.format(mosql.util.value(expected_text)))

    cur.execute('''select v from _test_value_in_mysql where k = 'mosql-2-ascii' ''')
    fetched_bytes, = cur.fetchone()
    fetched_text = fetched_bytes.decode('utf-8')

    assert fetched_text == expected_text

    cur.close()
    conn.close()
