#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import psycopg2
from mosql.query import insert, select, update, delete

class ConnContext(object):

    def __init__(self, *args, **kargs):
        self.conn = psycopg2.connect(*args, **kargs)

    def __enter__(self):
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()

class Person(dict):

    conn_context = ConnContext(host='127.0.0.1', database=os.environ['USER'])

    table_info = {'table': 'person'}
    select = select.breed(table_info)
    insert = insert.breed(table_info)

    def __init__(self, *args, **kargs):

        dict.__init__(self, *args, **kargs)

        row_info = self.table_info.copy()
        row_info['where'] = {'person_id': self['person_id']}
        self.update = update.breed(row_info)
        self.delete = delete.breed(row_info)

    @classmethod
    def create(cls, *args, **kargs):

        person = cls(*args, **kargs)

        with cls.conn_context as context:
            context.cur.execute(cls.insert(set=person))

        return person

    @classmethod
    def fetch(cls, person_id):

        with cls.conn_context as context:

            context.cur.execute(cls.select(where={'person_id': person_id}))

            if context.cur.rowcount:
                person = cls({desc.name: value for desc, value in zip(context.cur.description, context.cur.fetchone())})
            else:
                person = None

        return person

    def save(self):

        with self.conn_context as context:
            context.cur.execute(self.update(set=self))

    def remove(self):

        with self.conn_context as context:
            context.cur.execute(self.delete())

if __name__ == '__main__':

    dave = {
        'person_id': 'dave',
        'name'     : 'Dave',
    }


    # insert
    p = Person.create(dave)
    print p

    # select
    p = Person.fetch('dave')
    print p

    # update
    p['name'] = 'dave'
    p.save()
    #p = Person.fetch('dave') # if you insist
    print p

    # remove
    p.remove()
    p = Person.fetch('dave')
    print p

