from collections import OrderedDict

from nose.tools import eq_, assert_true

from mosql.compat import text_type
from mosql.query import insert


def test_simple_insert():
    mosky = OrderedDict([
        ('person_id', 'mosky'),
        ('name', 'Mosky Liu'),
    ])
    exp = 'INSERT INTO "person" ("person_id", "name") VALUES (\'mosky\', \'Mosky Liu\')'
    eq_(insert('person', mosky), exp)


def test_query_output():
    result = insert('message', {'always': u'Mosky \u2665'})
    assert_true(isinstance(result, text_type))  # We always output Unicode.
