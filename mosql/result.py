#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides useful :class:`Model` which let you commuicate with database
smoothly.

.. versionchanged:: 0.2
    It is totally rewritten, and it does **not** provide the
    backward-compatibility.
'''

__all__ = ['Model']

from itertools import groupby
from collections import Mapping
from pprint import pformat

from . import build
from . import util

def get_col_names(cur):
    return [row_desc[0] for row_desc in cur.description]

def hash_dict(d):
    return hash(frozenset(d.items()))

class Model(Mapping):
    '''The base model of result set.

    First, for creating connection, you need to override the two methods
    below:

    .. autosummary ::

        Model.getconn
        Model.putconn

    .. seealso ::

         Here are `examples
         <https://github.com/moskytw/mosql/tree/dev/examples>`_ which show how
         to use MoSQL with MySQL or PostgreSQL.

    Second, you may want to adjust the attributes :attr:`table`,
    :attr:`clauses`, :attr:`arrange_by`, :attr:`squash_by` or :attr:`ident_by`.

    1. The :attr:`Model.table` is the name of table.
    2. The :attr:`Model.clauses` lets you customize the queries, ex. order by,
       join statement, ... .
    3. The :attr:`Model.arrange_by` is need for :meth:`arrange` which arranges
       result set into models.
    4. The :attr:`Model.squash_by` lets it squash the columns which have
       duplicate values in rows.
    5. The last one, :attr:`Model.ident_by`, makes the :meth:`save` more
       efficiently.

    Then, make some queries to database:

    .. autosummary ::

        Model.select
        Model.insert
        Model.update
        Model.delete
        Model.arrange

    The :meth:`arrange` is like :meth:`select`, but it uses the
    :attr:`arrange_by` to arrange the result set.

    If you want to know what arguments you can use, see :mod:`mosql.build`.

    After select, there is a model instance. You can modifiy a model instance by
    below statements:

    ::

        m[squash_by_col_name] = val
        m.squash_by_col_name = val
        m[col_name, row_idx] = val

        # The following statements modifiy something, but the model can't record
        # the changes. It may be support in new version.
        m[col_name][row_idx] = val
        m.col_name[row_idx] = val

    When you finish your editing, use :meth:`save` to save the changes.

    You also have :meth:`pop` and :meth:`append` to maintain the rows in your
    model instance.

    It's all.
    '''

    # --- connection-related ---

    @classmethod
    def getconn(cls):
        '''It should return a connection.'''
        raise NotImplementedError('This method should return a connection.')

    @classmethod
    def putconn(cls, conn):
        '''It should accept a connection.'''
        raise NotImplementedError('This method should accept a connection.')

    dump_sql = False
    '''Set it True to make :meth:`Model.perform` dump the SQLs before it
    performs them.'''

    dry_run = False
    '''Set it True to make :meth:`Model.perform` rollback the changes after it
    performs them.'''

    @classmethod
    def perform(cls, sql_or_sqls):
        '''It executes SQL (str) or SQLs (seq) and return a cursor. :cls:`Model`
        uses it to perform every SQL.'''

        conn = cls.getconn()
        cur = conn.cursor()

        if isinstance(sql_or_sqls, basestring):
            sqls = [sql_or_sqls]
        else:
            sqls = sql_or_sqls

        if cls.dump_sql:
            print '--- SQL DUMP ---'
            for sql in sqls:
                print sql
            print '--- END ---'

        try:
            cur.execute('; '.join(sqls))
        except:
            conn.rollback()
            raise
        else:
            if cls.dry_run:
                conn.rollback()
            else:
                conn.commit()

        cls.putconn(conn)

        return cur

    # --- translate result set to a model or models ---

    col_names = tuple()

    @classmethod
    def load_rows(cls, col_names, rows):

        m = cls()
        m.col_names = col_names

        m.cols = dict((name, [
            row[i] for row in rows
        ]) for i, name in enumerate(m.col_names))

        return m

    @classmethod
    def load_cur(cls, cur):
        if cur.description is None:
            return None
        else:
            return cls.load_rows(get_col_names(cur), cur.fetchall())

    arrange_by = tuple()
    '''It defines how :meth:`Model.arrange` arrange result set. It should be
    column names in a tuple.'''

    @classmethod
    def arrange_rows(cls, col_names, rows):

        name_index_map = dict((name, i) for i, name  in enumerate(col_names))
        key_indexes = tuple(name_index_map[name] for name in cls.arrange_by)
        key_func = lambda row: tuple(row[i] for i in key_indexes)

        for _, rows in groupby(rows, key_func):
            yield cls.load_rows(col_names, list(rows))

    @classmethod
    def arrange_cur(cls, cur):
        return cls.arrange_rows(get_col_names(cur), cur.fetchall())

    # --- shortcuts of Python data structure -> SQL -> result set -> model ---

    table = ''
    '''It is used as the first argument of SQL builder.'''

    clauses = {}
    '''The additional clauses arguments for :mod:`mosql.build`. For an example:

    ::

        class Order(Model):
            ...
            table = 'order'
            clauses = dict(order_by=('created'))
            ...
    '''

    @classmethod
    def _query(cls, cur_handler, sql_builder, *args, **kargs):

        clauses = getattr(cls, 'clauses', None)
        if clauses:
            mixed_kargs = clauses.copy()
            if kargs:
                mixed_kargs.update(kargs)
        else:
            mixed_kargs = kargs

        return cur_handler(cls.perform(sql_builder(cls.table, *args, **mixed_kargs)))

    @classmethod
    def select(cls, *args, **kargs):
        '''It performs a select query and load result set into a model.'''
        return cls._query(cls.load_cur, build.select, *args, **kargs)

    @classmethod
    def arrange(cls, *args, **kargs):
        '''It performs a select query and arrange the result set into models.'''
        return cls._query(cls.arrange_cur, build.select, *args, **kargs)

    @classmethod
    def insert(cls, *args, **kargs):
        '''It performs an insert query and load result set into a model (if any).'''
        return cls._query(cls.load_cur, build.insert, *args, **kargs)

    @classmethod
    def update(cls, *args, **kargs):
        '''It performs an update query and load result set into a model (if any).'''
        return cls._query(cls.load_cur, build.update, *args, **kargs)

    @classmethod
    def delete(cls, *args, **kargs):
        '''It performs a delete query and load result set into a model (if any).'''
        return cls._query(cls.load_cur, build.delete, *args, **kargs)

    # --- read this model ---

    squash_by = set()
    '''It defines which column should be squash_by. It is better to use a set to
    enumerate the column names.'''

    def col(self, col_name):
        '''It returns the column you specified in this model.'''
        return self.cols[col_name]

    def __iter__(self):
        return (name for name in self.col_names)

    def __len__(self):
        return len(self.col_names)

    def row(self, row_idx):
        '''It returns the row you specified in this model.'''
        return [self.cols[col_name][row_idx] for col_name in self.col_names]

    def __getitem__(self, col_row):

        if isinstance(col_row, basestring):
            col_name = col_row
            if col_name in self.squash_by:
                col = self.cols[col_name]
                if col:
                    return col[0]
                else:
                    return None
            else:
                return self.cols[col_name]
        else:
            col_name, row_idx = col_row
            return self.cols[col_name][row_idx]

    def __getattr__(self, key):

        if key in self.cols:
            return self[key]
        else:
            raise AttributeError('attribute %r is not found' % key)

    def __setattr__(self, key, val):

        try:
            cols = object.__getattribute__(self, 'cols')
        except AttributeError:
            cols = None

        if cols and key in cols:
            self[key] = val
        else:
            object.__setattr__(self, key, val)

    # --- modifiy this model --- 

    ident_by = None
    '''It defines how to identify a row. It should be column names in a tuple.
    By default, it use all of the columns.'''

    def __init__(self):
        self.changes = []
        self.cols = {}

    def ident(self, row_idx):

        ident_by = self.ident_by
        if ident_by is None:
            ident_by = self.col_names

        ident = {}
        for col_name in ident_by:
            val = self.cols[col_name][row_idx]
            if val is util.default:
                raise ValueError("value of column %r is not decided yet." % col_name)
            ident[col_name] = val

        return ident

    def __setitem__(self, col_row, val):

        if isinstance(col_row, basestring):
            col_name = col_row
            if col_name in self.squash_by:
                for i in range(len(self.cols[col_name])):
                    self[col_name, i] = val
            else:
                raise TypeError("column %r is not squashed." % col_name)
        else:
            col_name, row_idx = col_row
            self.changes.append((self.ident(row_idx), {col_name: val}))
            self.cols[col_name][row_idx] = val

    def pop(self, row_idx=-1):
        '''It pops the row you specified in this model.'''

        self.changes.append((self.ident(row_idx), None))

        for col_name in self.col_names:
            self.cols[col_name].pop(row_idx)

    def append(self, row_map):
        '''It appends a row (dict) into model.'''

        row_map = row_map.copy()

        if not self.col_names:
            col_names = row_map.keys()
        else:
            col_names = self.col_names

        for col_name in col_names:

            if col_name in row_map:
                val = row_map[col_name]
            elif col_name in self.squash_by:
                val = row_map[col_name] = self.cols[col_name][0]
            else:
                val = row_map[col_name] = util.default

            self.cols[col_name] = val

        self.changes.append((None, row_map))

    def save(self):
        '''It saves changes.'''

        sqls = []

        if not self.changes:
            return

        for i, (cond, val) in enumerate(self.changes):

            if cond is None:
                sqls.append(build.insert(self.table, set=val, **self.clauses))
            elif val is None:
                sqls.append(build.delete(self.table, where=cond, **self.clauses))
            else:

                # find other update changes which cond is target_cond
                target_cond = cond
                cond_hash = hash_dict(target_cond)

                merged_val = val.copy()
                merged_idxs = []

                for j in range(i+1, len(self.changes)):

                    cond, val = self.changes[j]

                    # skip not update changes
                    if cond is None or val is None:
                        continue

                    if hash_dict(cond) == cond_hash:
                        merged_val.update(val)
                        merged_idxs.append(j)

                for j in reversed(merged_idxs):
                    self.changes.pop(j)

                sqls.append(build.update(self.table, where=target_cond, set=merged_val, **self.clauses))

        self.changes = []

        return self.perform(sqls)

    def __repr__(self):
        return pformat(dict(self))
