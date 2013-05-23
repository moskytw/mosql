#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from mosql.result2 import Model

class PostgreSQL(Model):
    getconn = classmethod(lambda cls: psycopg2.connect(database='mosky'))
    putconn = classmethod(lambda cls, conn: None)

class Person(PostgreSQL):
    clauses = dict(table='person')
    arrange_by = ('person_id', )
    squashed = ('person_id', 'name')
    ident_by = arrange_by

class Detail(PostgreSQL):
    clauses = dict(table='detail')
    arrange_by = ('person_id', 'key')
    squashed = arrange_by
    ident_by = ('detail_id', )

if __name__ == '__main__':

    print '# select all'
    person = Person.select()
    print person
    print person.cols
    print

    print '# select with a condition'
    person = Person.select(where={'person_id': 'mosky'})
    print person
    print person.cols
    print

    print '# powerful arrange'
    for person in Person.arrange():
        print person
    print

    print '# rename mosky'

    mosky = Person.select(where={'person_id': 'mosky'})
    mosky['name'] = 'Mosky Liu (renamed 1)'
    mosky['name'] = 'Mosky Liu (renamed 2)'
    mosky['name'] = 'Mosky Liu (renamed)'
    mosky.save()

    mosky = Person.select(where={'person_id': 'mosky'})
    print mosky['name']
    print

    from mosql.util import all

    print '# rename mosky back'
    mosky = Person.update(where={'person_id': 'mosky'}, set={'name': 'Mosky Liu'}, returning=all)
    print mosky
    print
