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

def make_identifier(s):

    # the mosql.util.identifier splits the input by . (dot), but we also wanna
    # test it, so write another one here.

    # mosql.util.qualifier encodes all the string into utf-8 now.
    if isinstance(s, unicode):
        s = s.encode('utf-8')

    return mosql.util.delimit_identifier(
        mosql.util.escape_identifier(s)
    )

def test_identifier_in_postgresql():

    # ensure we are in standard mode
    mosql.std.patch()

    conn = connect_to_postgresql()
    cur = conn.cursor()

    # The maximum identifier length in PostgreSQL is 63 bytes.
    # U+FFFF in utf-8 will have 3 bytes, so the best size each time is 10.
    # ref: http://www.postgresql.org/docs/9.3/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
    slice_size = 10

    # Test I-P-1: Identifier - PostgreSQL - BMP Chars with MoSQL's identifier function

    expected_sample_text = u''.join(unichr(i) for i in xrange(0x0001, 0xd800))
    # skip UTF-16 surrogates (U+D800-U+DBFF, U+DC00-U+DFFF) which cause
    # DataError in PostgreSQL.
    # ref: http://en.wikipedia.org/wiki/Plane_%28Unicode%29#Basic_Multilingual_Plane
    expected_sample_text += u''.join(unichr(i) for i in xrange(0xe000, 0xffff+1))

    for i in xrange(0, len(expected_sample_text), slice_size):

        sliced_expected_sample_text = expected_sample_text[i:i+slice_size]

        cur.execute('''
            create temporary table _test_identifier_in_postgresql (
                {} varchar(128) primary key
            )
        '''.format(make_identifier(sliced_expected_sample_text)))

        cur.execute('''
            select
                column_name
            from
                information_schema.columns
            where
                table_name = '_test_identifier_in_postgresql'
        ''')

        fetched_sample_bytes, = cur.fetchone()
        fetched_sample_text = fetched_sample_bytes.decode('utf-8')

        assert fetched_sample_text == sliced_expected_sample_text

        conn.rollback()

    # Test I-P-2: Identifier - PostgreSQL - Double ASCII Char's Dot Product
    # It will include '\' + any ASCII char, and '"' + any ASCII char.
    # dot product: dot_producr(XY, AB) = XAXBYAYB

    ascii_chars = [unichr(i) for i in xrange(0x01, 0x7f+1)]
    expected_sample_text = u''.join(a+b for a, b in product(ascii_chars, ascii_chars))

    for i in xrange(0, len(expected_sample_text), slice_size):

        sliced_expected_sample_text = expected_sample_text[i:i+slice_size]

        cur.execute('''
            create temporary table _test_identifier_in_postgresql (
                {} varchar(128) primary key
            )
        '''.format(make_identifier(sliced_expected_sample_text)))

        cur.execute('''
            select
                column_name
            from
                information_schema.columns
            where
                table_name = '_test_identifier_in_postgresql'
        ''')

        fetched_sample_bytes, = cur.fetchone()
        fetched_sample_text = fetched_sample_bytes.decode('utf-8')

        assert fetched_sample_text == sliced_expected_sample_text

        conn.rollback()

    cur.close()
    conn.close()
