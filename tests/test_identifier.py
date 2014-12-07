#!/usr/bin/env python
# -*- coding: utf-8 -*-

from getpass import getuser
from random import randrange
from itertools import product
import mosql.util
import mosql.mysql
import mosql.std

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

def make_identifier(s):

    # The mosql.util.identifier splits the input into table and column
    # identifier by . (dot), but here we want it to be a single identifier.

    # It is the default behavior of MoSQL: mosql.util.qualifier encodes all the
    # string into utf-8.
    if isinstance(s, unicode):
        s = s.encode('utf-8')

    return mosql.util.delimit_identifier(
        mosql.util.escape_identifier(s)
    )

# A `test_identifer_` covers around 80k characters. The databases all have the
# limitation on identifier's length, so we have to slice it to fit. It will take
# around 25 seconds to cover all slices. For making the routine unit test faster,
# set DENO (denominator) to skip part of the slices randomly.
#
# Set DENO as 1 to cover the all slices.

DENO = 100

# By default, the maximum identifier length in PostgreSQL is 63 bytes. The
# largest char in BMP is U+FFFF, and it will have 3 bytes in utf-8, so the best
# slice size is 21.
#
# ref: http://www.postgresql.org/docs/9.3/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS

POSTGRESQL_SLICE_SIZE = 21

def gen_slice_for_postgresql(s):

    for i in xrange(0, len(s), POSTGRESQL_SLICE_SIZE):
        yield s[i:i+POSTGRESQL_SLICE_SIZE]

def test_identifier_in_postgresql():

    mosql.std.patch()

    conn = connect_to_postgresql()
    cur = conn.cursor()

    # Test I-P-1: Identifier - PostgreSQL - The BMP Chars with MoSQL's Identifier Function
    #
    # It will include all BMP chars, except
    #
    # 1. the null byte (U+0000)
    # 2. utf-16 surrogates (U+D800-U+DBFF, U+DC00-U+DFFF)
    #
    # which are not valid identifier in PostgreSQL.
    #
    # ref: http://www.postgresql.org/docs/9.3/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS

    expected_text = u''.join(unichr(i) for i in xrange(0x0001, 0xd800))
    expected_text += u''.join(unichr(i) for i in xrange(0xe000, 0xffff+1))

    for sliced_expected_text in gen_slice_for_postgresql(expected_text):

        if randrange(DENO) != 0: continue

        cur.execute('''
            create temporary table _test_identifier_in_postgresql (
                {} varchar(128) primary key
            )
        '''.format(make_identifier(sliced_expected_text)))

        cur.execute('''
            select
                column_name
            from
                information_schema.columns
            where
                table_name = '_test_identifier_in_postgresql'
        ''')

        fetched_bytes, = cur.fetchone()
        fetched_text = fetched_bytes.decode('utf-8')

        assert fetched_text == sliced_expected_text

        conn.rollback()

    # Test I-P-2: Identifier - PostgreSQL - The Double ASCII Char's Dot Product
    #
    # It will include '\' + any ASCII char, and '"' + any ASCII char.
    #
    # dot product: dot_product(XY, AB) -> XAXBYAYB

    ascii_chars = [unichr(i) for i in xrange(0x01, 0x7f+1)]
    expected_text = u''.join(a+b for a, b in product(ascii_chars, ascii_chars))

    for sliced_expected_text in gen_slice_for_postgresql(expected_text):

        if randrange(DENO) != 0: continue

        cur.execute('''
            create temporary table _test_identifier_in_postgresql (
                {} varchar(128) primary key
            )
        '''.format(make_identifier(sliced_expected_text)))

        cur.execute('''
            select
                column_name
            from
                information_schema.columns
            where
                table_name = '_test_identifier_in_postgresql'
        ''')

        fetched_bytes, = cur.fetchone()
        fetched_text = fetched_bytes.decode('utf-8')

        assert fetched_text == sliced_expected_text

        conn.rollback()

    cur.close()
    conn.close()

def connect_to_mysql():

    import MySQLdb
    conn = MySQLdb.connect(user='root', db='root')

    cur = conn.cursor()

    # the columns: variable_name, value
    cur.execute('''show variables where variable_name = 'character_set_connection' ''')
    _, character_set_connection = cur.fetchone()
    assert character_set_connection == 'utf8'

    cur.close()

    return conn

# The maximum identifier length in MySQL is 64 characters, and identifier is
# stored in unicode.
#
# ref: http://dev.mysql.com/doc/refman/5.7/en/identifiers.html

MYSQL_SLICE_SIZE = 64

def gen_slice_for_mysql(s):

    for i in xrange(0, len(s), MYSQL_SLICE_SIZE):
        yield s[i:i+MYSQL_SLICE_SIZE]

# The MySQL's space chars which was found out by hand.
MYSQL_SPACE_CHAR_SET = set(u' \t\n\x0b\x0c\r')

def fix_mysql_space_char(s):

    # MySQL's database, table, and column names cannot end with space
    # characters.
    #
    # ref: http://dev.mysql.com/doc/refman/5.7/en/identifiers.html

    to_check_pos = -1
    while s[to_check_pos] in MYSQL_SPACE_CHAR_SET:
        to_check_pos -= 1

    # if no trailing space char
    if to_check_pos == -1:
        return s

    # the first pos of the trailing space chars
    pos = to_check_pos+1

    # move them to the starting
    return s[pos:]+s[:pos]

def test_identifier_in_mysql():

    # enable the MySQL mode
    mosql.mysql.patch()

    conn = connect_to_mysql()
    cur = conn.cursor()

    # Test I-M-1: Identifier - MySQL - The BMP Chars with MoSQL's Identifier Function
    #
    # It will include all BMP chars, except
    #
    # 1. the null byte (U+0000)
    # 2. the utf-16 low surrogates (U+DC00-U+DFFF)
    #
    # which are not valid identifier in MySQL.

    expected_text = u''.join(unichr(i) for i in xrange(0x0001, 0xdc00))
    expected_text += u''.join(unichr(i) for i in xrange(0xe000, 0xffff+1))

    for sliced_expected_text in gen_slice_for_mysql(expected_text):

        if randrange(DENO) != 0: continue

        sliced_expected_text = fix_mysql_space_char(sliced_expected_text)

        cur.execute('''
            create temporary table _test_identifier_in_mysql (
                {} varchar(128) primary key
            )
        '''.format(make_identifier(sliced_expected_text)))

        # ref: http://dev.mysql.com/doc/refman/5.7/en/explain.html
        cur.execute('desc _test_identifier_in_mysql')

        fetched_bytes, _, _, _, _, _ = cur.fetchone()
        fetched_text = fetched_bytes.decode('utf-8')

        assert fetched_text == sliced_expected_text

        cur.execute('drop table _test_identifier_in_mysql')

    # Test I-M-2: Identifier - MySQL - The Double ASCII Char's Dot Product
    #
    # It will include '\' + any ASCII char, and '`' + any ASCII char.
    #
    # dot product: dot_product(XY, AB) -> XAXBYAYB

    ascii_chars = [unichr(i) for i in xrange(0x01, 0x7f+1)]
    expected_text = u''.join(a+b for a, b in product(ascii_chars, ascii_chars))

    for sliced_expected_text in gen_slice_for_mysql(expected_text):

        if randrange(DENO) != 0: continue

        sliced_expected_text = fix_mysql_space_char(sliced_expected_text)

        cur.execute('''
            create temporary table _test_identifier_in_mysql (
                {} varchar(128) primary key
            )
        '''.format(make_identifier(sliced_expected_text)))

        cur.execute('desc _test_identifier_in_mysql')

        fetched_bytes, _, _, _, _, _ = cur.fetchone()
        fetched_text = fetched_bytes.decode('utf-8')

        assert fetched_text == sliced_expected_text

        cur.execute('drop table _test_identifier_in_mysql')

    cur.close()
    conn.close()
