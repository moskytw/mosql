#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import MySQL

class Person(MySQL):
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
    # MySQL doesn't support returning
    #mosky = Person.update({'person_id': 'mosky'}, set={'name': 'Mosky Liu'}, returning=star)
    Person.update({'person_id': 'mosky'}, set={'name': 'Mosky Liu'})
    mosky = Person.select({'person_id': 'mosky'})
    print mosky
    print


    import mosql.json as json

    print '# json'
    print json.dumps(mosky)
    print

    print '# mem test'

    def gen_rows():
        yield ['andy', 'Andy First']
        print 'mock cursor: yielded the first row'
        yield ['bob', 'Bob Second']
        print 'mock cursor: yielded the second row'
        yield ['cindy', 'Cindy Third']
        print 'mock cursor: yielded the thrid row'

    ps = Person.arrange_rows(['person_id', 'name'], gen_rows())
    print next(ps)
