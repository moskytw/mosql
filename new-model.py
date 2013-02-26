#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby, izip
import psycopg2


class ModelMeta(type):

    def __new__(meta, name, bases, attrs):

        Model = super(ModelMeta, meta).__new__(meta, name, bases, attrs)

        if Model.group is None:
            Model.group = Model.columns

        if Model.prikey is None:
            Model.prikey = Model.columns

        if Model.columns:
            Model.offsets = dict((k, i) for i, k in enumerate(Model.columns))
            Model.group_idxs = tuple(Model.offsets[k] for k in Model.group)
            Model.prikey_idxs = tuple(Model.offsets[k] for k in Model.prikey)

        return Model

class Model(dict):

    __metaclass__ = ModelMeta

    columns = None
    group   = None
    prikey  = None

    @classmethod
    def arrange(cls, rows):

        keyfunc = lambda row: tuple(row[i] for i in cls.group_idxs)
        for grouped_vals, rows in groupby(rows, keyfunc):

            model = cls()

            for i, name in enumerate(cls.group):
                model[name] = grouped_vals[i]

            for name, row in izip(cls.columns, izip(*rows)):
                if name not in model:
                    model[name] = row

            yield model

    def __init__(self, x=None):
        if x:
            super(Model, self).__init__(x)

    def items(self):
        return ((name, mode[name]) for name in self.columns)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, super(Model, self).__repr__())

class User(Model):
    columns = ('user_id', 'name')

class Detail(Model):
    columns = ('detail_id', 'user_id', 'key', 'val')
    group = ('user_id', 'key')

if __name__ == '__main__':

    from pprint import pprint

    conn = psycopg2.connect(database='mosky')
    cur = conn.cursor()

    cur.execute('select * from users order by user_id')
    for rows in User.arrange(cur.fetchall()):
        pprint(rows)
    print

    cur.execute('select * from details order by user_id, key, detail_id')
    for rows in Detail.arrange(cur.fetchall()):
        pprint(rows)
    print

    cur.execute("select * from details where user_id='mosky' and key='email' order by detail_id")
    detail = list(Detail.arrange(cur.fetchall()))[0]
    print detail
    # TODO:
    #detail['val'][0] = "rarely used"
    #del detail['val'][0]
    #detail.add_row('DEFALUT', 'me@mosky.tw')
    #print detail

    conn.close()
