#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mosql.result import Model
import psycopg2.pool

class PostgreSQLModel(Model):
    pool = psycopg2.pool.SimpleConnectionPool(1, 5, database='mosky')
    dump_sql = True

class Person(PostgreSQLModel):
    table_name = 'person'
    column_names = ('person_id', 'name')
    identify_by = ('person_id', )

class Detail(PostgreSQLModel):
    table_name = 'detail'
    column_names = ('detail_id', 'person_id', 'key', 'val')
    identify_by = ('detail_id', )
    group_by = ('person_id', 'key')

class PersonDetail(Detail):
    join_table_names = ('person', )
    column_names = ('person_id', 'detail_id', 'key', 'val', 'name')
    group_by = ('person_id', 'key', 'name')

if __name__ == '__main__':

    from pprint import pprint

    # --- test 1:1 table ---

    print '# Find everything in person'
    persons = Person.find()
    for person in persons:
        pprint(person)
    print

    print '# Find mosky in person'
    person = person.find(person_id='mosky')[0]
    print person
    print

    print '# Rename mosky'
    person.name = 'Mosky Liu 2'
    print person
    person.save()
    print

    print '# Rename mosky back'
    person['name'] = 'Mosky Liu'
    print person
    person.save()
    print

    # --- test 1:n (n:n) table ---

    print '# Find mosky and andy in detail'
    details = Detail.find(person_id=['mosky', 'andy'])
    for detail in details:
        pprint(detail)
    print

    print "# Find mosky's email"
    detail = detail.find(person_id='mosky', key='email')
    print detail
    print

    print '# Append a new email'
    detail.append(val='mosky@dummy.com')
    print detail

    try:
        detail.val[-1] = 'change it!'
    except ValueError:
        pass

    detail.save()
    print

    print "# Retrieve mosky's email"
    detail = detail.find(person_id='mosky', key='email')
    print detail
    print

    print '# Remoe the last row'
    detail.pop()
    print detail
    detail.save()
    print

    # --- test join ---

    print '# Test join'
    details = PersonDetail.find()
    for detail in details:
        pprint(detail)
    print
