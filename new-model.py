#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby, izip
import psycopg2

class Columns(object):

    def __init__(self, *names):
        self.names = names
        self.offsets = dict((k, i) for i, k in enumerate(names))

        self.primary_key = names
        self.primary_key_idxs = tuple(range(len(names)))

        self.to_group_names = names
        self.to_group_sets = set(names)
        self.to_group_names_idxs = self.primary_key_idxs

    def set_primary_key(self, *names):
        self.primary_key = names
        self.primary_key_idxs = tuple(self.offsets[k] for k in names)

    def set_to_group_names(self, *names):
        self.to_group_names = names
        self.to_group_sets = set(names)
        self.to_group_names_idxs = tuple(self.offsets[k] for k in names)

class Model(object):

    columns = None

    @classmethod
    def arrange(cls, rows):
        keyfunc = lambda row: tuple(row[i] for i in cls.columns.to_group_names_idxs)
        for grouped_vals, rows in groupby(rows, keyfunc):

            model = cls()

            for i, name in enumerate(cls.columns.to_group_names):
                setattr(model, name, grouped_vals[i])

            for name, row in izip(cls.columns.names, izip(*rows)):
                if not hasattr(model, name):
                    setattr(model, name, row)

            yield model

    @classmethod
    def to_ordered_tuples(cls, model):
        return ((name, getattr(model, name)) for name in cls.columns.names)

    @classmethod
    def to_dict(cls, model):
        return dict(cls.to_ordered_tuples(model))

    def __init__(self, d=None):
        if d:
            for k in d:
                setattr(self, k, d[v])

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__class__.to_dict(self))

class User(Model):
    columns = Columns('user_id', 'name')

class Detail(Model):
    columns = Columns('detail_id', 'user_id', 'key', 'val')
    columns.set_to_group_names('user_id', 'key')

if __name__ == '__main__':

    from pprint import pprint

    conn = psycopg2.connect(database='mosky')
    cur = conn.cursor()

    cur.execute('select * from users order by user_id')
    for rows in User.arrange(cur.fetchall()):
        pprint(rows)
    print

    cur.execute('select * from details order by user_id, key')
    for rows in Detail.arrange(cur.fetchall()):
        pprint(rows)
    print

    cur.execute("select * from details where user_id='mosky' and key='email'")
    detail = list(Detail.arrange(cur.fetchall()))[0]
    print detail
    # TODO:
    #detail.val[0] = "rarely used"
    #del detail.val[0]
    #detail.add_row('DEFALUT', 'me@mosky.tw')
    #print detail

    conn.close()
