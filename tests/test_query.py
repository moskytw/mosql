#!/usr/bin/env python
# -*- coding: utf-8 -*-


from collections import OrderedDict

from nose.tools import eq_, assert_raises

from mosql.query import select, insert, replace
from mosql.util import param, ___, raw, DirectionError, OperatorError, autoparam


def test_select_customize():
    gen = select('person', OrderedDict([
        ('name like', 'Mosky%'), ('age >', 20),
    ]))
    exp = 'SELECT * FROM "person" WHERE "name" LIKE \'Mosky%\' AND "age" > 20'
    eq_(gen, exp)


def test_select_customize_operator():
    gen = select('person', OrderedDict([
        (('name', 'like'), 'Mosky%'), (('age', '>'), 20)
    ]))
    exp = 'SELECT * FROM "person" WHERE "name" LIKE \'Mosky%\' AND "age" > 20'
    eq_(gen, exp)


def test_select_operationerror():
    with assert_raises(OperatorError) as cxt:
        select('person', {"person_id = '' OR true; --": 'mosky'})
    exp = "this operator is not allowed: \"= '' OR TRUE; --\""
    eq_(str(cxt.exception), exp)


def test_select_directionerror():
    with assert_raises(DirectionError) as cxt:
        select('person', {'name like': 'Mosky%'},
               order_by=('age ; DROP person; --', ))
    exp = "this direction is not allowed: '; DROP PERSON; --'"
    eq_(str(cxt.exception), exp)


def test_select_param():
    gen = select('table', OrderedDict([
        ('custom_param', param('my_param')), ('auto_param', autoparam),
        ('using_alias', ___),
    ]))
    exp = (
        'SELECT * FROM "table" WHERE "custom_param" = %(my_param)s '
        'AND "auto_param" = %(auto_param)s AND "using_alias" = %(using_alias)s'
    )
    eq_(gen, exp)


def test_insert_dict():
    gen = insert('person', OrderedDict([
        ('person_id', 'mosky'), ('name', 'Mosky Liu')
    ]))
    exp = ('INSERT INTO "person" ("person_id", "name") '
           'VALUES (\'mosky\', \'Mosky Liu\')')
    eq_(gen, exp)


def test_insert_returing():
    gen = insert('person', OrderedDict([
        ('person_id', 'mosky'), ('name', 'Mosky Liu'),
    ]), returning=raw('*'))
    exp = ('INSERT INTO "person" ("person_id", "name") '
           'VALUES (\'mosky\', \'Mosky Liu\') RETURNING *')
    eq_(gen, exp)


def test_replace():
    gen = replace('person', OrderedDict([
        ('person_id', 'mosky'), ('name', 'Mosky Liu')
    ]))
    exp = ('REPLACE INTO "person" ("person_id", "name") '
           'VALUES (\'mosky\', \'Mosky Liu\')')
    eq_(gen, exp)
