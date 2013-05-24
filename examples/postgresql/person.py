#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import PostgreSQL

class Person(PostgreSQL):
    table      = 'person'
    arrange_by = ('person_id', )
    squash_by  = set(['person_id', 'name'])
    ident_by   = arrange_by

if __name__ == '__main__':

    print '# select all'
    person = Person.select()
    print 'squashed:', person
    print 'actually:', person.cols
    print


    print '# select with a condition'
    person = Person.select({'person_id': 'mosky'})
    print 'squashed:', person
    print 'actually:', person.cols
    print


    print '# arrange entire table'
    for person in Person.arrange():
        print person
    print


    print '# arrange with a condition'
    for person in Person.arrange({'person_id': ('mosky', 'andy')}):
        print person
    print


    print '# rename mosky'

    mosky = Person.select({'person_id': 'mosky'})

    # model expands the change for columns squash_by
    mosky.name = '<ttypo>'
    mosky['name'] = '<renamed>'

    # model will merged the updates when save
    Person.dump_sql = True
    mosky.save()
    Person.dump_sql = False

    mosky = Person.select({'person_id': 'mosky'})
    print mosky.name
    print


    from mosql.util import all

    print '# rename mosky back'
    mosky = Person.update({'person_id': 'mosky'}, set={'name': 'Mosky Liu'}, returning=all)
    print mosky
    print


    import mosql.json as json

    print '# json'
    print json.dumps(mosky)
    print
