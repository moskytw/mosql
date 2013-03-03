#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Model', 'ModelMeta', 'Column', 'Row', 'Pool', 'Change']

'''It aims to help you to handle the result set.'''

from itertools import izip, groupby, repeat
from collections import MutableSequence, MutableMapping

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

from abc import ABCMeta

from . import common as sql

class Row(MutableMapping):
    '''A row proxy for a :py:class:`Model`.

    It implements :py:class:`MutableMapping`, but the setting item is the only mutable operation that is accepted.

    :param model: the model behind this proxy.
    :type model: :py:class:`Model`
    :param row_idx: the index of fixed row.
    :type row_idx: str
    '''

    def __init__(self, model, row_idx):
        self.model = model
        self.row_idx = row_idx

    def __len__(self):
        return len(self.model.column_names)

    def __iter__(self):
        for col_name in self.model.column_names:
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
    '''A column proxy for a :py:class:`Model`.

    It implements :py:class:`MutableSequence`, but the setting item is the only mutable operation that is accepted.

    :param model: the model behind this proxy.
    :type model: :py:class:`Model`
    :param col_name: the name of fixed column.
    :type col_name: str
    '''

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
    '''It records a single change on a row.

    :param row_identity_column_names: the column names which can identify a row.
    :type row_identity_column_names: tuple
    :param row_identity_values: the values which can identify a row.
    :type row_identity_values: tuple
    :param row: the changed row.
    :type row: dict
    '''

    def __init__(self, row_identity_column_names, row_identity_values, row):
        self.row_identity_column_names = row_identity_column_names
        self.row_identity_values = row_identity_values
        self.row = row

    def get_condition(self):
        '''It returns the condition in a dict, or None if it has not condition.

        :rtype: dict or None
        '''

        if self.row_identity_column_names is None or self.row_identity_values is None:
            return None
        else:
            return dict(izip(self.row_identity_column_names, self.row_identity_values))

class ModelMeta(ABCMeta):
    '''It will pre-process the class attributes of :py:class:`Model`.'''

    def __new__(meta, name, bases, attrs):

        Model = super(ModelMeta, meta).__new__(meta, name, bases, attrs)

        if not Model.group_by:
            Model.group_by = Model.column_names

        if not Model.identify_by:
            Model.identify_by = Model.column_names

        Model.column_offsets_map = dict((k, i) for i, k in enumerate(Model.column_names))

        group_by_idxs = tuple(Model.column_offsets_map[col_name] for col_name in Model.group_by)
        Model.group_by_key_func = staticmethod(lambda row: tuple(row[i] for i in group_by_idxs))

        if Model.join_table_names:
            import mosql.ext
            Model.join_caluses = ''.join(map(mosql.ext.join, Model.join_table_names))
        else:
            Model.join_caluses = ''

        for col_name in Model.column_names:
            if not hasattr(Model, col_name):
                setattr(Model, col_name,
                    # it is a colsure
                    (lambda x:
                        property(
                            lambda self: self.__getitem__(x),
                            lambda self, v: self.__setitem__(x, v),
                            lambda self: self.__delitem__(x)
                        )
                    )(col_name)
                )

        return Model

class Pool(object):
    '''An abstract class describes a protocol of connections pool used in :py:class:`Model`.

    .. note::
        If you are using `Psycopg <http://initd.org/psycopg/>`_, you can use its `Connections Pool <http://initd.org/psycopg/docs/pool.html>`_ directly.
    '''

    def getconn(self):
        '''Get a connection.

        :rtype: the `connection` which is defined in `Python DB API 2.0 : Connection Objects <http://www.python.org/dev/peps/pep-0249/#connection-objects>`_.
        '''
        pass

    def putconn(self, conn):
        '''Put a connection back.'''
        pass

Unknown = type('Unknown', (object, ), {
    '__nonzero__': lambda self: False,
    '__repr__'   : lambda self: 'Unknown',
})()
'''It represents a value decided by database.'''

class Model(MutableMapping):
    '''This class, which is the core of this module, provides a friendly interface to access result set and apply the changes to database.

    :param result_set: a result set, usually is a grouped result set.
    :type result_set: a cursor or tuples in a list

    If you don't know how to setup a model, this article can help you -- :ref:`tutorial-of-model`.

    The methods help you to retrieve the model(s):

    .. autosummary ::

        Model.find
        Model.seek

    If you want to modify something:

    .. autosummary ::

        Model.new
        Model.assume
        append
        pop
        clear

    It implements :py:class:`MutableMapping`, so just treat it as *dict*. But the `__delitem__` and `update` may not work as you think, because it is a result set from database. Try to use the above methods instead.

    .. versionadded :: 0.1.1
        It also supports to modify value with the attributes (ex. ``user.emails[0]`` is equal to ``user['emails'][0]``).

    Finally, I think you will want to save the changes:

    .. autosummary ::

        save

    '''

    __metaclass__ = ModelMeta

    pool = Pool()
    '''The connections pool described in :py:class:`Pool`.'''

    table_name = ''
    '''The name of main table.'''

    column_names = tuple()
    '''The name of columns.'''

    identify_by = tuple()
    '''The name of columns which can identify a row. Usually, it is the primary key.'''

    group_by = tuple()
    '''A model is consisted of one or more rows. It is used to group the result set.'''

    order_by = tuple()
    '''By default, it uses :py:attr:`Model.identify_by` to order the column values in a instance. It can override that.'''

    join_table_names = tuple()
    '''The tables you want to do the natural joins.'''
    # TODO: make user can write data via model which has join other tables

    dry_run = False
    '''It prevents the changes to be written into database.'''

    dump_sql = False
    '''Show the SQL it executed to stdout.'''

    @classmethod
    def find(cls, **where):
        '''It finds the rows matched `where` condition in the database.

        :param where: the condition of a SQL select.
        :type where: dict

        :rtype: :py:class:`Model` or Models

        It return a model if you gave all of the :py:attr:`Model.group_by` columns, and there is only one model after grouping.

        .. seealso ::
            How a dict to be rendered to the SQL --- :py:func:`mosql.common.select`.
        '''

        models = list(cls.seek(where=where, order_by=cls.group_by+(cls.order_by or cls.identify_by)))
        if len(models) == 1 and all(col_name in where for col_name in cls.group_by):
            return models[0]
        else:
            return models

    @classmethod
    def seek(cls, *args, **kargs):
        '''It is a shortcut for calling :py:func:`mosql.common.select` with values which have known, and it will group the result set.

        The all of the arguments will be passed to :py:func:`mosql.common.select`.

        :rtype: a generator of :py:class:`Model`
        '''

        return cls.group(cls.run(sql.select(cls.table_name, *args, select=cls.column_names, join=cls.join_caluses, **kargs)))

    @classmethod
    def group(cls, result_set):
        '''It groups the existent result set by :py:attr:`Model.group_by`.

        :param result_set: ungrouped result set.
        :type result_set: a cursor or tuples in a list
        :rtype: a generator of :py:class:`Model`
        '''

        for _, grouped_result_set in groupby(result_set, cls.group_by_key_func):
            yield cls(grouped_result_set)

    @classmethod
    def assume(cls, **model_dict):
        '''If you have known some value of a model, use it to make it be a model without doing a SQL select.

        :param model_dict: the part or full model.
        :type model_dict: dict
        :rtype: :py:class:`Model`
        '''

        cols = []
        for col_name in cls.column_names:

            x = model_dict.get(col_name, Unknown)

            if col_name in cls.group_by:
                cols.append(repeat(x))
            elif x is Unknown:
                cols.append(repeat(Unknown))
            else:
                cols.append(x)

        if all(isinstance(x, repeat) for x in cols):
            cols = [[next(x)] for x in cols]

        return cls(izip(*cols))

    @classmethod
    def new(cls, **model_dict):
        '''It works like :py:meth:`Model.assume`, but it treats the rows as new. You can use :py:meth:`Model.save` to save them.

        :param model_dict: the part or full model.
        :type model_dict: dict
        :rtype: :py:class:`Model`
        '''

        model = cls.assume(**model_dict)

        for row in model.rows():
            model.changes[len(model.changes)] = Change(None, None, dict((k, v) for k, v in row.items() if v is not Unknown))

        return model

    def __init__(self, result_set):

        self.row_len = 0
        self.elems = []
        for result in result_set:
            self.elems.extend(result)
            self.row_len += 1

        self.proxies = {}
        self.changes = OrderedDict()

        self.grouped_row = {}
        self.grouped_row = dict((col_name, self[col_name][0]) for col_name in self.group_by)

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
        '''It adds a row into model.

        :param row: the row you want to add.
        :type row: dict
        '''

        for col_name in self.group_by:
            if col_name not in row:
                row[col_name] = self.grouped_row[col_name]

        self.changes[len(self.changes)] = Change(None, None, row)

        for col_name in self.column_names:
            self.elems.append(row.get(col_name, Unknown))
        self.row_len += 1

    def pop(self, row_idx=-1):
        '''It removes a row from this model.

        :rtype: list
        '''

        row_identity_values = self.get_row_identity_values(row_idx)
        self.changes[row_identity_values] = Change(self.identify_by, row_identity_values, None)

        self.row_len -= 1
        col_len = len(self.column_names)
        start = row_idx * col_len

        row = self.elems[start:start+col_len]
        del self.elems[start:start+col_len]

        return row

    def clear(self):
        '''It removes all of the row in this model.'''

        for i in xrange(self.row_len):
            self.pop()

    def rows(self):
        '''It returns a iterable which traverses all of the rows.

        :rtype: a generator of :py:class:`Row`
        '''

        for i in xrange(self.row_len):
            yield self[i]

    def save(self):
        '''It saves the changes which cached in model.

        :rtype: cursor
        '''

        sqls = []
        for change in self.changes.values():
            cond = change.get_condition()
            if cond is None:
                sqls.append(sql.insert(self.table_name, change.row))
            elif change.row is None:
                sqls.append(sql.delete(self.table_name, cond))
            else:
                sqls.append(sql.update(self.table_name, cond, change.row))
        self.changes.clear()
        return self.run(sqls)

    @classmethod
    def run(cls, sql_or_sqls):
        '''It runs a SQL or SQLs with the :py:attr:`Model.pool` you specified.

        :param sql_or_sqls: a string SQL or iterable SQLs.
        :type sql_or_sqls: str or list

        :rtype: cursor'''

        if isinstance(sql_or_sqls, basestring):
            sqls = [sql_or_sqls]
        else:
            sqls = sql_or_sqls

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

if __name__ == '__main__':
    pass
