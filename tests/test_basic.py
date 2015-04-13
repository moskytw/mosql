from collections import OrderedDict

from nose.tools import eq_

from mosql.query import insert


def test_simple_insert():
    mosky = OrderedDict([
        ('person_id', 'mosky'),
        ('name', 'Mosky Liu'),
    ])
    exp = 'INSERT INTO "person" ("person_id", "name") VALUES (\'mosky\', \'Mosky Liu\')'
    eq_(insert('person', mosky), exp)
