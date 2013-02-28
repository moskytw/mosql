#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import izip, groupby
from collections import MutableSequence, MutableMapping

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

from abc import ABCMeta

import sql

class Row(MutableMapping):

    def __init__(self, model, row_idx):
        self.model = model
        self.row_idx = row_idx

    def __len__(self):
        return len(self.model.column_names)

    def __iter__(self):
        for col_name in self.column_names:
            yield col_name

    def __getitem__(self, col_name):
        return self.model.__getelem__(self.row_idx, col_name)

    def __setitem__(self, col_name, val):
        self.model.__setelem__(self.row_idx, col_name, val)

    def __delitem__(self, col_name):
        raise TypeError('this operation is not supported')

    def __repr__(self):
        return repr(dict(self))

class Column(MutableSequence):

    def __init__(self, model, col_name):
        self.model = model
        self.col_name = col_name

    def __len__(self):
        return self.model.row_len

    def __iter__(self):
        for i in xrange(self.model.row_len):
            yield self[i]

    def __getitem__(self, row_idx):
        return self.model.__getelem__(row_idx, self.col_name)

    def __setitem__(self, row_idx, val):
        self.model.__setelem__(row_idx, self.col_name, val)

    def __delitem__(self, col_name):
        raise TypeError('this operation is not supported')

    def insert(self, col_name):
        raise TypeError('this operation is not supported')

    def __repr__(self):
        return repr(list(self))

class Change(object):

    def __init__(self, row_identity_column_names, row_identity_values, row):
        self.row_identity_column_names = row_identity_column_names
        self.row_identity_values = row_identity_values
        self.row = row

    def get_condition(self):
        if self.row_identity_column_names is None or self.row_identity_values is None:
            return None
        else:
            return dict(izip(self.row_identity_column_names, self.row_identity_values))

class ModelMeta(ABCMeta):

    def __new__(meta, name, bases, attrs):

        Model = super(ModelMeta, meta).__new__(meta, name, bases, attrs)

        if not Model.group_by:
            Model.group_by = Model.column_names

        Model.column_offsets_map = dict((k, i) for i, k in enumerate(Model.column_names))
        group_by_idxs = tuple(Model.column_offsets_map[col_name] for col_name in Model.group_by)
        Model.group_by_key_func = staticmethod(lambda row: tuple(row[i] for i in group_by_idxs))

        return Model

class Pool(object):

    def getconn(self):
        pass

    def putconn(self, conn):
        pass

Unknown = type('Unknown', (object, ), {
    '__nonzero__': lambda self: False,
    '__repr__'   : lambda self: 'Unknown',
})()

class Model(MutableMapping):

    __metaclass__ = ModelMeta

    pool = Pool()
    table_name = ''
    column_names = tuple()
    identify_by = tuple()
    order_by = tuple()
    group_by = tuple()

    join = ''

    dry_run = False
    dump_sql = False

    @classmethod
    def find(cls, **where):
        models = list(cls.seek(where=where, order_by=cls.group_by+cls.order_by))
        if len(models) == 1 and all(col_name in where for col_name in cls.group_by):
            return models[0]
        else:
            return models

    @classmethod
    def seek(cls, *args, **kargs):
        return cls.group(cls.run(sql.select(cls.table_name, *args, join=cls.join, **kargs)))

    @classmethod
    def group(cls, rows):
        for grouped_row_vals, rows in groupby(rows, cls.group_by_key_func):
            yield cls(dict(izip(cls.group_by, grouped_row_vals)), rows)

    def __init__(self, grouped_row, rows):

        self.grouped_row = grouped_row

        self.row_len = 0
        self.elems = []
        for row in rows:
            self.elems.extend(row)
            self.row_len += 1

        self.proxies = {}
        self.changes = OrderedDict()

    def __len__(self):
        return len(self.column_names)

    def __iter__(self):
        for col_name in self.column_names:
            yield col_name

    def __getitem__(self, x):

        if x in self.grouped_row:
            return self.grouped_row[x]

        if isinstance(x, int) and x < 0:
            x += self.row_len

        if x in self.proxies:
            return self.proxies[x]

        if isinstance(x, str):
            Proxy = Column
        else:
            Proxy = Row

        self.proxies[x] = proxy = Proxy(self, x)
        return proxy

    def __setitem__(self, grouped_col_name, val):

        row_identity_values = tuple(self.grouped_row[col_name] for col_name in self.group_by)
        if row_identity_values in self.changes:
            self.changes[row_identity_values].row[grouped_col_name] = val
        else:
            self.changes[row_identity_values] = Change(self.group_by, row_identity_values, {grouped_col_name: val})

        self.grouped_row[grouped_col_name] = val

    def __getelem__(self, row_idx, col_name):
        return self.elems[row_idx*len(self.column_names)+self.column_offsets_map[col_name]]

    def get_row_identity_values(self, row_idx):
        row_identity_values = tuple(self[row_idx][col_name] for col_name in self.identify_by)
        if any(val is Unknown for val in row_identity_values):
            raise ValueError("this row can't be identified; it has unknown value")
        return row_identity_values

    def __setelem__(self, row_idx, col_name, val):

        row_identity_values = self.get_row_identity_values(row_idx)
        if row_identity_values in self.changes:
            self.changes[row_identity_values].row[col_name] = val
        else:
            self.changes[row_identity_values] = Change(self.identify_by, row_identity_values, {col_name: val})

        self.elems[row_idx*len(self.column_names)+self.column_offsets_map[col_name]] = val

    def __delitem__(self, col_name):
        raise TypeError('this operation is not supported')

    def append(self, **row):

        for col_name in self.group_by:
            if col_name not in row:
                row[col_name] = self.grouped_row[col_name]

        self.changes[len(self.changes)] = Change(None, None, row)

        for col_name in self.column_names:
            self.elems.append(row.get(col_name, Unknown))
        self.row_len += 1

    def pop(self, row_idx=-1):
        row_identity_values = self.get_row_identity_values(row_idx)
        self.changes[row_identity_values] = Change(self.identify_by, row_identity_values, None)

        self.row_len -= 1
        col_len = len(self.column_names)
        start = row_idx * col_len
        del self.elems[start:start+col_len]

    def clear(self):
        for i in xrange(self.row_len):
            self.pop()

    def rows(self):
        for i in xrange(self.row_len):
            return self[i]

    def save(self):
        sqls = []
        for change in self.changes.values():
            cond = change.get_condition()
            if cond is None:
                sqls.append(sql.insert(self.table_name, change.row))
            elif change.row is None:
                sqls.append(sql.delete(self.table_name, cond))
            else:
                sqls.append(sql.update(self.table_name, cond, change.row))
        return self.run(sqls)

    @classmethod
    def run(cls, sqls):

        if isinstance(sqls, basestring):
            sqls = [sqls]

        if cls.dump_sql:
            from pprint import pprint
            pprint(sqls)

        conn = cls.pool.getconn()
        cur = conn.cursor()

        if not cls.dry_run:
            try:
                cur.execute('; '.join(sqls))
            except:
                conn.rollback()
                raise
            else:
                conn.commit()

        cls.pool.putconn(conn)

        return cur

    def __repr__(self):
        return repr(dict(self))

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

class PersonDetail(PostgreSQLModel):
    table_name = 'detail'
    join = sql.join('person')
    column_names = ('person_id', 'detail_id', 'key', 'val', 'name')
    identify_by = ('detail_id', )
    group_by = ('person_id', 'key')

if __name__ == '__main__':

    from pprint import pprint

    # --- test 1:1 table ---

    persons = Person.find()
    print

    for person in persons:
        pprint(person)
    print

    person['name'] = 'New Name'
    print person
    print

    #person.clear()
    #print person
    #print
    # psycopg2.IntegrityError: update or delete on table "person" violates foreign key constraint "detail_person_id_fkey" on table "detail"
    # DETAIL:  Key (person_id)=(mosky) is still referenced from table "detail".

    person.save()
    print

    # --- test 1:n (n:n) table ---

    details = Detail.find(person_id=['mosky', 'andy'])
    print

    for detail in details:
        pprint(detail)
    print

    detail['val'][0] = 'new@email.com'
    print detail
    print

    detail.pop(0)
    print detail
    print

    detail.append(val='new@email.com')
    print detail
    print

    try:
        detail['val'][-1] = 'change it!'
    except ValueError:
        pass

    detail.save()
    print

    detail = Detail.find(person_id='mosky', key='email')

    detail['val'][0] = 'new@email.com'
    print detail
    print

    detail.pop(0)
    print detail
    print

    detail.append(val='new@email.com')
    print detail
    print

    try:
        detail['val'][-1] = 'change it!'
    except ValueError:
        pass

    detail.save()
    print

    # --- test join ---

    details = PersonDetail.find()
    print

    for detail in details:
        pprint(OrderedDict(detail))
    print

    detail['val'][0] = 'new@email.com'
    print detail
    print

    detail.pop(0)
    print detail
    print

    detail.append(val='new@email.com')
    print detail
    print

    try:
        detail['val'][-1] = 'change it!'
    except ValueError:
        pass

    detail.save()
    print
