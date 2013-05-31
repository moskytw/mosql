#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import MySQL

class Person(MySQL):

    # the name of table
    table      = 'person'

    # The result set is converted to column-oriented model, so the columns are
    # lists. You can use this attribute to squash some of them into a single
    # value:
    #squashed = set(['person_id', 'name'])
    # set `squash_all` True to squash all of the columns
    squash_all = True

    # The class method, `arrange`, uses this attribute to arrange result set.
    arrange_by = ('person_id', )

    # It specifies the columns which will be use to prepare the conditions.
    ident_by   = arrange_by

    # the other clauses you want to put in the queries
    clauses    = dict(order_by=arrange_by)

if __name__ == '__main__':

    # If you want to see the SQLs it generates:
    #Person.dump_sql = True

    print '# The Model of Mosky'
    print
    mosky = Person.select({'person_id': 'mosky'})
    print mosky
    print

    print '# Access the Model, and Re-Select'
    print
    print mosky.person_id
    print mosky['name']
    print

    print '# Rename Mosky, and Re-Select'
    print

    mosky.name = 'Yiyu Lui'

    # The previous one has some typo.
    mosky.name = 'Yiyu Liu'

    # The two changes will be merge into only an update.
    mosky.save()

    # Re-selecting is not necessary. I just wanna show you the db is really
    # changed. Here I use where for short.
    print Person.where(person_id='mosky')
    print

    print '# Rename Her Back'
    print
    mosky['name'] = 'Mosky Liu'
    mosky.save()
    print Person.where(person_id='mosky')
    print

    print '# Arrange Rows into Models'
    print
    for person in Person.arrange({'person_id': ('mosky', 'andy')}):
        print person
    # or use ``Person.find(person_id=('mosky', 'andy'))`` in for-loop
    print

    print '# Insert a New Person'
    print
    d = {'person_id': 'new'}
    Person.insert(d, on_duplicate_key_update=d)
    new_person = Person.where(person_id='new')
    print new_person
    print

    print '# Delete the New Person'
    print
    new_person = Person.delete({'person_id': 'new'})
    print new_person
    print
