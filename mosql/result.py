#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
.. deprecated:: 0.6
    It will be removed because it is which MoSQL shouldn't do. If you need a
    model, just write a class with :mod:`mosql.query` instead.

It provides useful :class:`Model` which let you commuicate with database
smoothly.

.. versionchanged:: 0.2
    It is totally rewritten, and it does **not** provide the
    backward-compatibility.
'''

__all__ = ['Model']

from itertools import groupby
from collections import Mapping, Sequence
from pprint import pformat

from . import build
from . import util

class ColProxy(Sequence):

    def __init__(self, model, col_name):
        self.model = model
        self.col_name = col_name

    def __len__(self):
        return self.model.cols[self.col_name].__len__()

    def __iter__(self):
        return self.model.cols[self.col_name].__iter__()

    def __contains__(self, elem):
        return self.model.cols[self.col_name].__contains__(elem)

    def __getitem__(self, row_idx):
        return self.model.cols[self.col_name][row_idx]

    def __setitem__(self, row_idx, val):
        self.model.set(self.col_name, row_idx, val)

    def __repr__(self):
        return pformat(list(self))

class RowProxy(Mapping):

    def __init__(self, model, row_idx):
        self.model = model
        self.row_idx = row_idx

    def __len__(self):
        return len(self.model.cols)

    def __iter__(self):
        return (col_name for col_name in self.model.cols)

    def __contains__(self, elem):
        return elem in self.model.cols

    def __getitem__(self, col_name):
        return self.model.cols[col_name][self.row_idx]

    def __setitem__(self, col_name, val):
        self.model.set(col_name, self.row_idx, val)

    def __getattr__(self, key):

        if key in self.model.cols:
            return self[key]
        else:
            raise AttributeError('%r object has no attribute %r' % (self.__class__.__name__, key))

    # It makes __setattr__ work.
    model = None

    def __setattr__(self, key, val):

        if self.model and key in self.model.cols:
            self[key] = val
        else:
            object.__setattr__(self, key, val)

    def __repr__(self):
        return pformat(dict(self))

def get_col_names(cur):
    return [row_desc[0] for row_desc in cur.description]

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
    :attr:`clauses`, :attr:`arrange_by`, :attr:`squashed` or :attr:`ident_by`.

    1. The :attr:`Model.table` is the name of table.
    2. The :attr:`Model.clauses` lets you customize the default clauses of this
       model, ex. order by, join statement, ... .
    3. The :attr:`Model.arrange_by` is need for :meth:`arrange` which arranges
       result set into models.
    4. The :attr:`Model.squashed` defines the columns you want to squash.
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

    The following two methods treat all of the keyword arguments as `where`. It
    makes statements simpler.

    .. autosummary ::

        Model.where
        Model.find

    If you want to know what arguments you can use, see :mod:`mosql.build`.

    After select, there is a model instance. You can access the data in a model
    instance by the below statements:

    ::

        m['col_name'][row_idx]
        m.col_name[row_idx]

        m[row_idx]['col_name']
        m[row_idx].col_name

        m['col_name']
        m.col_name

        m['col_name'][row_idx] = val
        m.col_name[row_idx] = val

        m[row_idx]['col_name'] = val
        m[row_idx].col_name = val

        # if this column is squashed
        m['col_name'] = val
        m.col_name = val

    .. versionchanged :: 0.4
        Added this format, ``m[row_idx]['col_name']``.

    The :meth:`Model.rows()` also works well:

    ::

        for row in m.rows():
            print row.col_name
            print row['col_name']
            row.col_name = val
            row['col_name'] = val

    .. versionadded:: 0.4

    When you finish your editing, use :meth:`save` to save the changes.

    You also have :meth:`pop` and :meth:`append` (or :meth:`add`) to maintain
    the rows in your model instance, or create a empty model by :meth:`new`.
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

    @classmethod
    def getcur(cls, conn):
        '''It lets you customize your cursor. By default, it return a cursor by the following code:

        ::

            return conn.cursor()

        .. versionadded :: 0.4
        '''
        return conn.cursor()

    dump_sql = False
    '''Set it True to make :meth:`Model.perform` dump the SQLs before it
    performs them.'''

    dry_run = False
    '''Set it True to make :meth:`Model.perform` rollback the changes after it
    performs them.'''

    @classmethod
    def perform(cls, sql=None, param=None, params=None, proc=None, sqls=None):
        '''It performs SQL, SQLs or/and procedure with parameter(s).

        .. versionchanged:: v0.5
            It supports to use parameter and call procedure.
        '''

        conn = cls.getconn()
        cur = cls.getcur(conn)

        if cls.dump_sql:
            if sql or sqls:
                print '--- SQL DUMP ---'
                for sql in (sqls or [sql]):
                    print sql
                print '--- END ---'
            if proc:
                print '--- SQL DUMP ---'
                print 'callproc: %r' % proc
                print '--- END ---'
            if param or params:
                print '--- PARAMETER DUMP ---'
                for param in (params or [param]):
                    print param
                print '--- END ---'

        _do = cur.execute
        _param = param
        if params:
            _do = cur.executemany
            _param = params

        try:
            if sql:
                _do(sql, _param)
            if sqls:
                for sql in sqls:
                    _do(sql, _param)
            if proc:
                cur.callproc(proc, _param)
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

    def __init__(self, defaults=None):
        self.row_len = 0
        self.cols = {}
        self.changes = []
        self.proxies = {}
        self.defaults = defaults or {}

    @classmethod
    def new(cls, **defaults):
        '''Create a empty model instance with the key arguments as the default
        values. It is a shortcut for initialization method.

        A typical usage:

        >>> m = Model.new(id='mosky')
        >>> m.add(email='mosky.tw@gmail.com')
        >>> m.add(email='mosky.liu@pinkoi.com')
        >>> print m
        {'email': ['mosky.tw@gmail.com', 'mosky.liu@pinkoi.com'],
         'id': ['mosky', 'mosky']}

        .. versionadded:: v0.5
        '''
        return cls(defaults)

    @classmethod
    def load_rows(cls, col_names, rows):

        m = cls()

        m.cols = dict((col_name, []) for col_name in col_names)

        for row in rows:
            for col_name, col_val in zip(col_names, row):
                m.cols[col_name].append(col_val)
                if m.squash_all or col_name in m.squashed:
                    m.defaults[col_name] = col_val
            m.row_len += 1

        return m

    @classmethod
    def load_cur(cls, cur):

        # The `description` is None if use an insert, update or delete without
        # `returning`.
        # The `rowcount` is 0 if no row returns from a select.
        if cur.rowcount == 0 or cur.description is None:
            return None
        else:
            return cls.load_rows(get_col_names(cur), cur)

    arrange_by = tuple()
    '''It defines how :meth:`Model.arrange` arrange result set. It should be
    column names in a tuple.'''

    @classmethod
    def arrange_rows(cls, col_names, rows):

        name_index_map = dict((name, i) for i, name  in enumerate(col_names))
        key_indexes = tuple(name_index_map.get(name) for name in cls.arrange_by)

        # use util.default as the hyper None
        key_func = lambda row: tuple(
            row[i] if i is not None else util.default
            for i in key_indexes
        )

        for _, rows in groupby(rows, key_func):
            yield cls.load_rows(col_names, rows)

    @classmethod
    def arrange_cur(cls, cur):
        return cls.arrange_rows(get_col_names(cur), cur)

    # --- shortcuts of Python data structure -> SQL -> result set -> model ---

    table = ''
    '''It is used as the first argument of SQL builder.'''

    clauses = {}
    '''The additional clauses arguments for :mod:`mosql.build`. For example:

    ::

        class Order(Model):
            ...
            table = 'order'
            clauses = dict(order_by=('created',))
            ...
    '''

    @classmethod
    def _query(cls, cur_handler, sql_builder, *args, **kargs):

        if cls.clauses:
            mixed_kargs = cls.clauses.copy()
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
    def where(cls, **where):
        '''It uses keyword arguments as `where` and passes to :meth:`select`.'''
        return cls.select(where=where)

    @classmethod
    def arrange(cls, *args, **kargs):
        '''It performs a select query and arrange the result set into models.'''
        return cls._query(cls.arrange_cur, build.select, *args, **kargs)

    @classmethod
    def find(cls, **where):
        '''It uses keyword arguments as `where` and passes to :meth:`arrange`.'''
        return cls.arrange(where=where)

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

    def __iter__(self):
        return (name for name in self.cols)

    def __len__(self):
        return len(self.cols)

    def rows(self):
        '''It generates the proxy for each row.

        .. versionadded:: 0.4
        '''
        return (self[i] for i in xrange(self.row_len))

    def proxy(self, name_or_idx):

        if name_or_idx in self.proxies:
            return self.proxies[name_or_idx]
        else:
            Proxy = ColProxy if isinstance(name_or_idx, basestring) else RowProxy
            self.proxies[name_or_idx] = proxy = Proxy(self, name_or_idx)
            return proxy

    squashed = set()
    '''It defines which columns should be squashed. It is better to use a set to
    enumerate the names of columns.'''

    squash_all = False
    '''If you want to squash all of columns, set it True.

    .. versionadded :: 0.4
    '''

    def __getitem__(self, name_or_idx):

        if self.squash_all or name_or_idx in self.squashed:
            try:
                return self.cols[name_or_idx][0]
            except IndexError:
                return None
        else:
            return self.proxy(name_or_idx)

    def __getattr__(self, key):

        if key in self.cols:
            return self[key]
        else:
            raise AttributeError('%r object has no attribute %r' % (self.__class__.__name__, key))

    # It makes __setattr__ work.
    cols = None

    def __setattr__(self, key, val):

        if self.cols and key in self.cols:
            self[key] = val
        else:
            object.__setattr__(self, key, val)

    # --- modifiy this model --- 

    ident_by = None
    '''It defines how to identify a row. It should be column names in a tuple.'''

    def ident(self, row_idx=None):

        # use what columns to build where clause
        if row_idx is None:
            # change this value in all rows in this model
            cond_col_names = self.arrange_by or self.cols
            row_idx = 0
        else:
            cond_col_names = self.ident_by or self.cols

        # build the where
        cond = {}
        for cond_col_name in cond_col_names:

            try:
                cond_val = self.cols[cond_col_name][row_idx]
            except IndexError:
                raise IndexError('row index out of range')
            except KeyError:
                raise KeyError('the column is not existent: %r' % cond_col_name)

            if cond_val is util.default:
                raise ValueError('cond_value of column %r is unknown' % cond_col_name)

            cond[cond_col_name] = cond_val

        return cond

    def __setitem__(self, col_name, val):

        if self.squash_all or col_name in self.squashed:
            self.set(col_name, None, val)
        else:
            raise TypeError("column %r is not squashed." % col_name)

    def set(self, col_name, row_idx, val):

        self.changes.append((self.ident(row_idx), {col_name: val}))

        if row_idx is None:
            for row_idx in xrange(len(self.cols[col_name])):
                self.cols[col_name][row_idx] = val
        else:
            self.cols[col_name][row_idx] = val

    def pop(self, row_idx=-1):
        '''It pops the row you specified in this model.

        .. versionchanged :: v0.4
            It returns the row poped in a dict.
        '''

        self.changes.append((self.ident(row_idx), None))

        poped_row = {}
        for col_name in self.cols:
            poped_row[col_name] = self.cols[col_name].pop(row_idx)

        self.row_len -= 1

        return poped_row

    def append(self, row_map):
        '''It appends a row into model.

        The `row_map` should be a mapping which includes full or part values of
        a row. If you provide a part of row, the row will be filled with 1.
        defaults (by :meth:`__init__`, :meth:`new` or squashed columns) 2. :data:`~mosql.util.default` in order.

        See the :meth:`new` for the typical usage.
        '''

        row_map = row_map.copy()

        for col_name in set(row_map.keys()+self.cols.keys()+self.defaults.keys()):

            if col_name in row_map:
                val = row_map[col_name]
            elif col_name in self.defaults:
                val = row_map[col_name] = self.defaults[col_name]
            else:
                val = row_map[col_name] = util.default

            if col_name in self.cols:
                self.cols[col_name].append(val)
            else:
                self.cols[col_name] = [val]

        self.row_len += 1

        self.changes.append((None, row_map))

    def add(self, **row_map):
        '''It is a shortcut for :meth:`Model.append`.

        .. versionadded:: v0.5
        '''
        self.append(row_map)

    def save(self):
        '''It saves the changes.

        When it encounters an update, it uses :attr:`ident_by` to build where.
        If the column updated is squashed, it will use the :attr:`arrange_by`
        instead. But if the `ident_by` or `arrange_by` is not set, it will use
        all of the columns

        For efficiency, it will merge the updates which have same condition into
        a single update.

        .. versionchanged:: v0.5.1
            It uses `arrange_by` for the column squashed.
        '''

        if not self.changes:
            return

        sqls = []

        for i, (cond, val) in enumerate(self.changes):

            if cond is None:
                sqls.append(build.insert(self.table, set=val, **self.clauses))
            elif val is None:
                sqls.append(build.delete(self.table, where=cond, **self.clauses))
            else:

                # find other update changes which cond is target_cond
                target_cond = cond

                merged_val = val.copy()
                merged_idxs = []

                for j in range(i+1, len(self.changes)):

                    cond, val = self.changes[j]

                    # skip not update changes
                    if cond is None or val is None:
                        continue

                    if cond == target_cond:
                        merged_val.update(val)
                        merged_idxs.append(j)

                for j in reversed(merged_idxs):
                    self.changes.pop(j)

                sqls.append(build.update(self.table, where=target_cond, set=merged_val, **self.clauses))

        self.changes = []

        return self.perform(sqls=sqls)

    def clear(self):
        '''It pops all of the row in this model.

        .. versionchanged:: v0.5.1
            It doesn't call :meth:`pop` anymore. It clears this model directly.

        .. versionadded:: v0.5
        '''
        self.changes.append((self.ident(), None))
        self.cols.clear()

    def __repr__(self):
        return pformat(dict(self))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
