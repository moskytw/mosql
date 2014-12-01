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

    # We will use the MoSQL in standard mode, so check it.
    # After PostgreSQL 9.1, the default is on.
    cur.execute('show standard_conforming_strings')
    standard_conforming_strings, = cur.fetchone()
    assert standard_conforming_strings == 'on'

    # We will try to insert all chars from U+0001 to U+FFFF.
    cur.execute('show server_encoding')
    server_encoding, = cur.fetchone()
    assert server_encoding == 'UTF8'

    # MoSQL builds utf-8 string for now.
    cur.execute('show client_encoding')
    client_encoding, = cur.fetchone()
    assert client_encoding == 'UTF8'

    cur.close()

    return conn

def test_value_in_postgresql():

    # ensure we are in standard mode
    mosql.std.patch()

    conn = connect_to_postgresql()
    cur = conn.cursor()

    cur.execute('''
        create temporary table _test_value_in_postgresql (
            k varchar(128) primary key,
            v text
        )
    ''')


    # Test V-P-1: Value - PostgreSQL - BMP Chars

    expected_sample_text = u''.join(unichr(i) for i in xrange(0x0001, 0xd800))
    # skip UTF-16 surrogates (U+D800-U+DBFF, U+DC00-U+DFFF) which cause
    # DataError in PostgreSQL.
    # ref: http://en.wikipedia.org/wiki/Plane_%28Unicode%29#Basic_Multilingual_Plane
    expected_sample_text += u''.join(unichr(i) for i in xrange(0xe000, 0xffff+1))


    # Test V-P-1-1: Value - PostgreSQL - BMP Chars - Raw SQL

    cur.execute('''
        insert into
            _test_value_in_postgresql
        values (
            'raw-sql-bmp',
            %s
        )
    ''', (expected_sample_text, ))

    cur.execute('''select v from _test_value_in_postgresql where k = 'raw-sql-bmp' ''')
    fetched_sample_bytes, = cur.fetchone()
    fetched_sample_text = fetched_sample_bytes.decode('utf-8')

    assert fetched_sample_text == expected_sample_text


    # Test V-P-1-2: Value - PostgreSQL BMP Chars - MoSQL's value function

    cur.execute('''
        insert into
            _test_value_in_postgresql
        values (
            'mosql-bmp',
            {}
        )
    '''.format(mosql.util.value(expected_sample_text)))

    cur.execute('''select v from _test_value_in_postgresql where k = 'mosql-bmp' ''')
    fetched_sample_bytes, = cur.fetchone()
    fetched_sample_text = fetched_sample_bytes.decode('utf-8')

    assert fetched_sample_text == expected_sample_text


    # Test V-P-2: Value - PostgreSQL - Double ASCII Char's Dot Product
    # It will include '\' + any ASCII char, and "'" + any ASCII char.
    # dot product: dot_producr(XY, AB) = XAXBYAYB

    ascii_chars = [unichr(i) for i in xrange(0x01, 0x7f+1)]
    expected_sample_text = u''.join(a+b for a, b in product(ascii_chars, ascii_chars))


    # Test V-P-2-1: Value - PostgreSQL - Double ASCII Char's Dot Product - Raw SQL

    cur.execute('''
        insert into
            _test_value_in_postgresql
        values (
            'raw-sql-2-ascii',
            %s
        )
    ''', (expected_sample_text, ))

    cur.execute('''select v from _test_value_in_postgresql where k = 'raw-sql-2-ascii' ''')
    fetched_sample_bytes, = cur.fetchone()
    fetched_sample_text = fetched_sample_bytes.decode('utf-8')

    assert fetched_sample_text == expected_sample_text


    # Test V-P-2-2: Value - PostgreSQL - Double ASCII Char's Dot Product - MoSQL's value function

    cur.execute('''
        insert into
            _test_value_in_postgresql
        values (
            'mosql-2-ascii',
            {}
        )
    '''.format(mosql.util.value(expected_sample_text)))

    cur.execute('''select v from _test_value_in_postgresql where k = 'mosql-2-ascii' ''')
    fetched_sample_bytes, = cur.fetchone()
    fetched_sample_text = fetched_sample_bytes.decode('utf-8')

    assert fetched_sample_text == expected_sample_text


    cur.close()
    conn.close()

def connect_to_mysql():

    import MySQLdb
    conn = MySQLdb.connect(user='root', db='root')

    cur = conn.cursor()

    # We will try to insert all chars from U+0000 to U+FFFF.
    cur.execute('''show variables where variable_name = 'character_set_database' ''')
    _, character_set_database = cur.fetchone()
    assert character_set_database == 'utf8'

    # MoSQL builds utf-8 string for now, and
    # it should be utf8 to avoid the issue which will be introduced by the
    # encodings which allow ASCII \ within a multibyte character, e.g., big5.

    # PostgreSQL doesn't need to cosider it. Because, by default, PostgreSQL's
    # backslash_quote is safe_encoding which allows to use \ to escape quotes in
    # string literal only if client encoding does not allow ASCII \ within a
    # multibyte character.

    cur.execute('''show variables where variable_name = 'character_set_connection' ''')
    _, character_set_connection = cur.fetchone()
    assert character_set_connection == 'utf8'

    cur.close()

    return conn

def test_value_in_mysql():

    # enable MySQL mode
    mosql.mysql.patch()

    conn = connect_to_mysql()
    cur = conn.cursor()

    cur.execute('''
        create temporary table _test_value_in_mysql (
            k varchar(128) primary key,
            v mediumtext
        )
    ''')


    # Test V-M-1: Value - MySQL - BMP Chars
    # ref: http://en.wikipedia.org/wiki/Plane_(Unicode)#Basic_Multilingual_Plane

    # MySQL's first range is larger than PostgreSQL. MySQL's range includes
    # 1. the null byte (U+0000)
    # 2. the UTF-16's high surrogates (U+D800-U+DBFF)
    expected_sample_text = u''.join(unichr(i) for i in xrange(0x0000, 0xdc00))
    expected_sample_text += u''.join(unichr(i) for i in xrange(0xe000, 0xffff+1))


    # Test V-M-1-1: Value - MySQL - BMP Chars - Raw SQL

    cur.execute('''
        insert into
            _test_value_in_mysql
        values (
            'raw-sql-bmp',
            %s
        )
    ''', (expected_sample_text, ))

    cur.execute('''select v from _test_value_in_mysql where k = 'raw-sql-bmp' ''')
    fetched_sample_bytes, = cur.fetchone()
    fetched_sample_text = fetched_sample_bytes.decode('utf-8')

    assert fetched_sample_text == expected_sample_text


    # Test V-M-1-2: Value - MySQL - BMP Chars - MoSQL's value function

    cur.execute('''
        insert into
            _test_value_in_mysql
        values (
            'mosql-bmp',
            {}
        )
    '''.format(mosql.util.value(expected_sample_text)))

    cur.execute('''select v from _test_value_in_mysql where k = 'mosql-bmp' ''')
    fetched_sample_bytes, = cur.fetchone()
    fetched_sample_text = fetched_sample_bytes.decode('utf-8')

    assert fetched_sample_text == expected_sample_text


    # Test V-M-2: Value - MySQL - Double ASCII Char's Dot Product
    # It will include '\' + any ASCII char, and "'" + any ASCII char.
    # dot product: dot_producr(XY, AB) = XAXBYAYB

    ascii_chars = [unichr(i) for i in xrange(0x01, 0x7f+1)]
    expected_sample_text = u''.join(a+b for a, b in product(ascii_chars, ascii_chars))


    # Test V-M-2-1: Value - MySQL - Double ASCII Char's Dot Product - Raw SQL

    cur.execute('''
        insert into
            _test_value_in_mysql
        values (
            'raw-sql-2-ascii',
            %s
        )
    ''', (expected_sample_text, ))

    cur.execute('''select v from _test_value_in_mysql where k = 'raw-sql-2-ascii' ''')
    fetched_sample_bytes, = cur.fetchone()
    fetched_sample_text = fetched_sample_bytes.decode('utf-8')

    assert fetched_sample_text == expected_sample_text


    # Test V-M-2-2: Value - MySQL - Double ASCII Char's Dot Product - MoSQL's value function

    cur.execute('''
        insert into
            _test_value_in_mysql
        values (
            'mosql-2-ascii',
            {}
        )
    '''.format(mosql.util.value(expected_sample_text)))

    cur.execute('''select v from _test_value_in_mysql where k = 'mosql-2-ascii' ''')
    fetched_sample_bytes, = cur.fetchone()
    fetched_sample_text = fetched_sample_bytes.decode('utf-8')

    assert fetched_sample_text == expected_sample_text


    cur.close()
    conn.close()
