from collections import OrderedDict
from datetime import date

from nose.tools import eq_, assert_true, assert_false

from mosql.compat import binary_type, text_type
from mosql.util import (
    autoparam, build_set, build_where, param, ___,
    _is_iterable_not_str,
)


def test_is_iterable_not_str():
    # Iterable objects.
    assert_true(_is_iterable_not_str([]))
    assert_true(_is_iterable_not_str(tuple()))
    assert_true(_is_iterable_not_str({}))
    assert_true(_is_iterable_not_str(set()))

    # Strings are iterable, but not included.
    assert_false(_is_iterable_not_str(''))
    assert_false(_is_iterable_not_str(b''))
    assert_false(_is_iterable_not_str(u''))
    assert_false(_is_iterable_not_str(binary_type()))
    assert_false(_is_iterable_not_str(text_type()))


def test_build_where():
    gen = build_where(OrderedDict([
        ('detail_id', 1), ('age >= ', 20), ('created', date(2013, 4, 16)),
    ]))
    eq_(gen, '"detail_id" = 1 AND "age" >= 20 AND "created" = \'2013-04-16\'')


def test_build_where_operator():
    gen = build_where(OrderedDict([
        ('detail_id', 1), (('age', '>='), 20), ('created', date(2013, 4, 16)),
    ]))
    eq_(gen, '"detail_id" = 1 AND "age" >= 20 AND "created" = \'2013-04-16\'')


def test_build_where_prepared():
    gen = build_where(OrderedDict([
        ('custom_param', param('my_param')), ('auto_param', autoparam),
        ('using_alias', ___),
    ]))
    exp = ('"custom_param" = %(my_param)s AND "auto_param" = %(auto_param)s '
           'AND "using_alias" = %(using_alias)s')
    eq_(gen, exp)


def test_build_set():
    gen = build_set(OrderedDict([
        ('a', 1), ('b', True), ('c', date(2013, 4, 16)),
    ]))
    eq_(gen, '"a"=1, "b"=TRUE, "c"=\'2013-04-16\'')


def test_build_set_prepared():
    gen = build_set(OrderedDict([
        ('custom_param', param('myparam')), ('auto_param', autoparam),
    ]))
    eq_(gen, '"custom_param"=%(myparam)s, "auto_param"=%(auto_param)s')
