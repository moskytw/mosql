#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Do not import unicode_literal in this module! Tests below depend on binary
# str literals on Python 2.
from nose.tools import eq_

from mosql.query import insert


def test_text_input():
    exp = u'INSERT INTO "message" ("always") VALUES (\'😘モスキー\')'
    eq_(insert('message', {'always': u'😘モスキー'}), exp)


def test_binary_input():
    """Binary input should always be decoded with UTF-8, not platform encoding.
    """
    gen = insert('message', {
        'always': b'\xf0\x9f\x98\x98\xe3\x83\xa2\xe3\x82\xb9\xe3\x82\xad\xe3\x83\xbc',
    })
    exp = u'INSERT INTO "message" ("always") VALUES (\'😘モスキー\')'
    eq_(gen, exp)


def test_str_input():
    """Test str literals.

    On Python 3 this is identical to the text input test, but on Python 2 this
    ensures MoSQL can handle binary str literal input. The input is always
    decoded with UTF-8, not platform encoding, so this should work on all
    platforms.
    """
    exp = u'INSERT INTO "message" ("always") VALUES (\'😘モスキー\')'
    eq_(insert('message', {'always': '😘モスキー'}), exp)
