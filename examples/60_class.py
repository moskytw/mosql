#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from mosql.query import insert, select, update, delete
from mosql.db import Database, one_to_dict

class Person(dict):

    db = Database(psycopg2, host='127.0.0.1')
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
        with cls.db as cur:
            cur.execute(cls.insert(set=person))
        return person

    @classmethod
    def fetch(cls, person_id):
        with cls.db as cur:
            cur.execute(cls.select(where={'person_id': person_id}))
            if cur.rowcount:
                person = cls(one_to_dict(cur))
            else:
                person = None
        return person

    def save(self):
        with self.db as cur:
            cur.execute(self.update(set=self))

    def remove(self):
        with self.db as cur:
            cur.execute(self.delete())

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

    # delete
    p.remove()
    p = Person.fetch('dave')
    print p

