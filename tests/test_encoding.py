#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Do not import unicode_literal in this module! Tests below depend on binary
# str literals on Python 2.
from nose.tools import eq_

from mosql.compat import PY2
from mosql.query import insert
from mosql.util import param, raw


def test_text_input():
    exp = u'INSERT INTO "message" ("always") VALUES (\'😘モスキー\')'
    eq_(insert('message', {'always': u'😘モスキー'}), exp)


if PY2:
    def test_binary_input():
        """Binary input should always be decoded with UTF-8 on Python 2.
        """
        gen = insert('message', {
            'always': b'\xf0\x9f\x98\x98\xe3\x83\xa2\xe3\x82\xb9\xe3\x82\xad\xe3\x83\xbc',
        })
        exp = u'INSERT INTO "message" ("always") VALUES (\'😘モスキー\')'
        eq_(gen, exp)

    def test_str_input():
        """Test str literals on Python 2.

        On Python 2 this ensures MoSQL can handle binary str literal input. The
        input should always be decoded with UTF-8, not platform encoding, so
        this works on all OSs.
        """
        exp = u'INSERT INTO "message" ("always") VALUES (\'😘モスキー\')'
        eq_(insert('message', {'always': '😘モスキー'}), exp)

    def test_raw_repr():
        eq_(repr(raw('Mosky')), "raw(u'Mosky')")

    def test_param_repr():
        eq_(repr(param('Mosky')), "param(u'Mosky')")

else:
    def test_str_input():
        """Test str literals on Python 3.

        This should yield identical results to test_text_input because the u
        prefix has not effect on Python 3.
        """
        exp = 'INSERT INTO "message" ("always") VALUES (\'😘モスキー\')'
        eq_(insert('message', {'always': '😘モスキー'}), exp)

    def test_raw_repr():
        eq_(repr(raw('Mosky')), "raw('Mosky')")

    def test_param_repr():
        eq_(repr(param('Mosky')), "param('Mosky')")
