#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import MySQL

class Person(MySQL):
    clauses = dict(table='person')
    arrange_by = ('person_id', )
    squashed = ('person_id', 'name')
    ident_by = arrange_by

if __name__ == '__main__':

    print '# select all'
    person = Person.select()
    print 'squashed:', person
    print 'actually:', person.cols
    print


    print '# select with a condition'
    person = Person.select(where={'person_id': 'mosky'})
    print 'squashed:', person
    print 'actually:', person.cols
    print


    print '# arrange entire table'
    for person in Person.arrange():
        print person
    print


    print '# arrange with a condition'
    for person in Person.arrange(where={'person_id': ('mosky', 'andy')}):
        print person
    print


    print '# rename mosky'

    mosky = Person.select(where={'person_id': 'mosky'})
    # model expands the change for columns squashed
    mosky.name = 'Mosky Liu (renamed 1)'
    # setitem or setattr are also accepted
    mosky['name'] = 'Mosky Liu (renamed 2)'
    mosky.name = 'Mosky Liu (renamed)'
    # model will merged the updates when save
    Person.dump_sql = True
    mosky.save()
    Person.dump_sql = False

    mosky = Person.select(where={'person_id': 'mosky'})
    print mosky.name
    print


    from mosql.util import all

    print '# rename mosky back'
    # MySQL doesn't support returning
    #mosky = Person.update(where={'person_id': 'mosky'}, set={'name': 'Mosky Liu'}, returning=all)
    Person.update(where={'person_id': 'mosky'}, set={'name': 'Mosky Liu'})
    mosky = Person.select(where={'person_id': 'mosky'})
    print mosky
    print


    import mosql.json as json

    print '# json'
    print json.dumps(mosky)
    print
