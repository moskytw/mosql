#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import PostgreSQL

class Person(PostgreSQL):
    clauses = dict(table='person')
    arrange_by = ('person_id', )
    squashed = ('person_id', 'name')
    ident_by = arrange_by

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

    print '# powerful arrange with a condition'
    for person in Person.arrange(where={'person_id': ('mosky', 'andy')}):
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
