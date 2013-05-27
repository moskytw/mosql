#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import PostgreSQL

class Person(PostgreSQL):
    table      = 'person'
    arrange_by = ('person_id', )
    squashed   = set(['person_id', 'name'])
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

    # where is almost same as select
    mosky = Person.where(person_id='mosky')

    # model expands the change for columns squashed
    mosky.name = '<ttypo>'
    mosky['name'] = '<renamed>'

    # model will merged the updates when save
    Person.dump_sql = True
    mosky.save()
    Person.dump_sql = False

    mosky = Person.select({'person_id': 'mosky'})
    print mosky.name
    print


    from mosql.util import star

    print '# rename mosky back'
    mosky = Person.update({'person_id': 'mosky'}, set={'name': 'Mosky Liu'}, returning=star)
    print mosky
    print


    import mosql.json as json

    print '# json'
    print json.dumps(mosky)
    print

    print '# mem test'

    def gen_rows():
        yield ['a', 'i am a']
        print 'mock cursor: yielded the first row'
        yield ['b', 'i am b']
        print 'mock cursor: yielded the second row'
        yield ['c', 'i am c']
        print 'mock cursor: yielded the thrid row'

    ps = Person.arrange_rows(['person_id', 'name'], gen_rows())
    print next(ps)
