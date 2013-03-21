#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mosql.result import Model
import psycopg2.pool

class PostgreSQLModel(Model):
    pool = psycopg2.pool.SimpleConnectionPool(1, 5, database='mosky')
    dump_sql = True

class Person(PostgreSQLModel):
    table_name = 'person'
    identify_by = ('person_id', )

#Person = PostgreSQLModel.customize(
#    table_name   = 'person',
#    column_names = ('person_id', 'name'),
#    identify_by = ('person_id', ),
#)

#class Detail(PostgreSQLModel):
#    table_name = 'detail'
#    column_names = ('detail_id', 'person_id', 'key', 'val')
#    identify_by = ('detail_id', )
#    group_by = ('person_id', 'key')

#class PersonDetail(Detail):
#    join_table_names = ('person', )
#    column_names = ('person_id', 'detail_id', 'key', 'val', 'name')
#    group_by = ('person_id', 'key', 'name')

if __name__ == '__main__':

    for model in Person.find():
        print model
