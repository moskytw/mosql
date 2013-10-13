#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
.. deprecated:: 0.6
    Use :mod:`mosql.query` instead.

It contains the common SQL builders.

.. versionchanged:: 0.2
    It is renamed from ``common``.

.. versionchanged:: 0.1.6
    It is rewritten for using new :mod:`mosql.util`, but it is compatible with
    old version.

.. autosummary ::
    select
    insert
    update
    delete
    join
    or_

It is designed for building the standard SQL statement and tested in PostgreSQL.

.. note::
    If you use MySQL, here is a patch for MySQL --- :mod:`mosql.mysql`.
'''

__all__ = ['select', 'insert', 'delete', 'update', 'join', 'or_']

from .util import *

# defines formatting chains
single_value      = (value, )
single_identifier = (identifier, )
identifier_list   = (identifier, concat_by_comma)
column_list       = (identifier, concat_by_comma, paren)
value_list        = (value, concat_by_comma, paren)
where_list        = (build_where, )
set_list          = (build_set, )
statement_list    = (concat_by_space, )

# insert

insert    = Clause('insert into', single_identifier)
columns   = Clause('columns'    , column_list, hidden=True)
values    = Clause('values'     , value_list)
returning = Clause('returning'  , identifier_list)
on_duplicate_key_update = Clause('on duplicate key update', set_list)

insert_into_stat = Statement([insert, columns, values, returning, on_duplicate_key_update])

def insert(table, set=None, values=None, **clauses_args):
    '''It generates the SQL statement, ``insert into ...``.

    The following usages generate the same SQL statement:

    >>> print insert('person', {'person_id': 'mosky', 'name': 'Mosky Liu'})
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    >>> print insert('person', (('person_id', 'mosky'), ('name', 'Mosky Liu')))
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    >>> print insert('person', ('person_id', 'name'), ('mosky', 'Mosky Liu'))
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    The columns is ignorable:

    >>> print insert('person', values=('mosky', 'Mosky Liu'))
    INSERT INTO "person" VALUES ('mosky', 'Mosky Liu')

    The :func:`insert`, :func:`update` and :func:`delete` support ``returning``.

    >>> print insert('person', {'person_id': 'mosky', 'name': 'Mosky Liu'}, returning=raw('*'))
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu') RETURNING *

    The MySQL-specific "on duplicate key update" is also supported:

    >>> print insert('person', values=('mosky', 'Mosky Liu'), on_duplicate_key_update={'name': 'Mosky Liu'})
    INSERT INTO "person" VALUES ('mosky', 'Mosky Liu') ON DUPLICATE KEY UPDATE "name"='Mosky Liu'
    '''

    clauses_args['insert into'] = table

    if values is None:
        if hasattr(set, 'items'):
            pairs = set.items()
        else:
            pairs = set
        clauses_args['columns'], clauses_args['values'] = zip(*pairs)
    else:
        clauses_args['columns'] = set
        clauses_args['values']  = values

    if 'on_duplicate_key_update' in clauses_args:
        clauses_args['on duplicate key update'] = clauses_args['on_duplicate_key_update']
        del clauses_args['on_duplicate_key_update']

    return insert_into_stat.format(clauses_args)

# select

select   = Clause('select'  , identifier_list)
from_    = Clause('from'    , identifier_list)
joins    = Clause('joins'   , statement_list, hidden=True)
where    = Clause('where'   , where_list)
group_by = Clause('group by', identifier_list)
having   = Clause('having'  , where_list)
order_by = Clause('order by', identifier_list)
limit    = Clause('limit'   , single_value)
offset   = Clause('offset'  , single_value)

select_stat = Statement([select, from_, joins, where, group_by, having, order_by, limit, offset])

def select(table, where=None, select=None, **clauses_args):
    '''It generates the SQL statement, ``select ...`` .

    .. versionchanged:: 0.1.6
        The clause argument, ``join``, is renamed to ``joins``.

    The following usages generate the same SQL statement.

    >>> print select('person', {'person_id': 'mosky'})
    SELECT * FROM "person" WHERE "person_id" = 'mosky'

    >>> print select('person', (('person_id', 'mosky'), ))
    SELECT * FROM "person" WHERE "person_id" = 'mosky'

    It detects the dot in an identifier:

    >>> print select('person', select=('person.person_id', 'person.name'))
    SELECT "person"."person_id", "person"."name" FROM "person"

    Building prepare statement with :class:`mosql.util.param`:

    >>> print select('table', {'custom_param': param('my_param'), 'auto_param': param, 'using_alias': ___})
    SELECT * FROM "table" WHERE "auto_param" = %(auto_param)s AND "using_alias" = %(using_alias)s AND "custom_param" = %(my_param)s

    You can also specify the ``group_by``, ``having``, ``order_by``, ``limit``
    and ``offset`` in the keyword arguments. Here are some examples:

    >>> print select('person', {'name like': 'Mosky%'}, group_by=('age', ))
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' GROUP BY "age"

    >>> print select('person', {'name like': 'Mosky%'}, order_by=('age', ))
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age"

    >>> print select('person', {'name like': 'Mosky%'}, order_by=('age desc', ))
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC

    >>> print select('person', {'name like': 'Mosky%'}, order_by=('age ; DROP person; --', ))
    Traceback (most recent call last):
        ...
    OptionError: this option is not allowed: '; DROP PERSON; --'

    .. seealso ::
        The options allowed --- :attr:`mosql.util.allowed_options`.

    >>> print select('person', {'name like': 'Mosky%'}, limit=3, offset=1)
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' LIMIT 3 OFFSET 1

    The operators are also supported:

    >>> print select('person', {'person_id': ('andy', 'bob')})
    SELECT * FROM "person" WHERE "person_id" IN ('andy', 'bob')

    >>> print select('person', {'name': None})
    SELECT * FROM "person" WHERE "name" IS NULL

    >>> print select('person', {'name like': 'Mosky%', 'age >': 20})
    SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'

    >>> print select('person', {"person_id = '' OR true; --": 'mosky'})
    Traceback (most recent call last):
        ...
    OperatorError: this operator is not allowed: "= '' OR TRUE; --"

    .. seealso ::
        The operators allowed --- :attr:`mosql.util.allowed_operators`.

    If you want to use functions, wrap it with :class:`mosql.util.raw`:

    >>> print select('person', select=raw('count(*)'), group_by=('age', ))
    SELECT count(*) FROM "person" GROUP BY "age"

    .. warning ::
        You have responsibility to ensure the security if you use :class:`mosql.util.raw`.

    .. seealso ::
        How it builds the where clause --- :func:`mosql.util.build_where`
    '''

    clauses_args['from']   = table
    clauses_args['where']  = where
    clauses_args['select'] = star if select is None else select

    if 'order_by' in clauses_args:
        clauses_args['order by'] = clauses_args['order_by']
        del clauses_args['order_by']

    if 'group_by' in clauses_args:
        clauses_args['group by'] = clauses_args['group_by']
        del clauses_args['group_by']

    return select_stat.format(clauses_args)

# update

update = Clause('update', single_identifier)
set    = Clause('set'   , set_list)

update_stat = Statement([update, set, where, returning])

def update(table, where=None, set=None, **clauses_args):
    '''It generates the SQL statement, ``update ...`` .

    The following usages generate the same SQL statement.

    >>> print update('person', {'person_id': 'mosky'}, {'name': 'Mosky Liu'})
    UPDATE "person" SET "name"='Mosky Liu' WHERE "person_id" = 'mosky'

    >>> print update('person', (('person_id', 'mosky'), ), (('name', 'Mosky Liu'),) )
    UPDATE "person" SET "name"='Mosky Liu' WHERE "person_id" = 'mosky'

    .. seealso ::
        How it builds the where clause --- :func:`mosql.util.build_set`
    '''

    clauses_args['update'] = table
    clauses_args['where']  = where
    clauses_args['set']    = set

    return update_stat.format(clauses_args)

# delete from

delete = Clause('delete from', single_identifier)

delete_stat = Statement([delete, where, returning])

def delete(table, where=None, **clauses_args):
    '''It generates the SQL statement, ``delete from ...`` .

    The following usages generate the same SQL statement.

    >>> print delete('person', {'person_id': 'mosky'})
    DELETE FROM "person" WHERE "person_id" = 'mosky'

    >>> print delete('person', (('person_id', 'mosky'), ))
    DELETE FROM "person" WHERE "person_id" = 'mosky'
    '''

    clauses_args['delete from'] = table
    clauses_args['where'] = where

    return delete_stat.format(clauses_args)

# join

join  = Clause('join' , single_identifier)
type  = Clause('type' , tuple(), hidden=True)
on    = Clause('on'   , (build_on, ))
using = Clause('using', column_list)

join_stat = Statement([type, join, on, using])

def join(table, using=None, on=None, type=None, **clauses_args):
    '''It generates the SQL statement, ``... join ...`` .

    .. versionadded :: 0.1.6

    >>> print select('person', joins=join('detail'))
    SELECT * FROM "person" NATURAL JOIN "detail"

    >>> print select('person', joins=join('detail', using=('person_id', )))
    SELECT * FROM "person" INNER JOIN "detail" USING ("person_id")

    >>> print select('person', joins=join('detail', on={'person.person_id': 'detail.person_id'}))
    SELECT * FROM "person" INNER JOIN "detail" ON "person"."person_id" = "detail"."person_id"

    >>> print select('person', joins=join('detail', type='cross'))
    SELECT * FROM "person" CROSS JOIN "detail"

    .. seealso ::
        How it builds the where clause --- :func:`mosql.util.build_on`
    '''

    clauses_args['join'] = table
    clauses_args['using'] = using
    clauses_args['on'] = on

    if not type:
        if using or on:
            clauses_args['type'] = 'INNER'
        else:
            clauses_args['type'] = 'NATURAL'
    else:
        clauses_args['type'] = type.upper()

    return join_stat.format(clauses_args)

# or

def or_(*conditions):
    '''It concats the conditions by ``OR``.

    .. versionadded :: 0.1.6

    >>> print or_({'person_id': 'andy'}, {'person_id': 'bob'})
    "person_id" = 'andy' OR "person_id" = 'bob'
    '''

    return concat_by_or(build_where(c) for c in conditions)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # benchmark

    #from timeit import timeit
    #from functools import partial
    #timeit = partial(timeit, number=100000)

    #import mosql.util

    #print timeit(lambda: select('person', {'name': 'Mosky Liu'}, ('person_id', 'name'), limit=10, order_by='person_id'))
    ## -> 4.97957897186

    #print timeit(lambda: select('person', {'name': 'Mosky Liu'}, ('person.person_id', 'person.name'), limit=10, order_by='person_id'))
    ## -> 5.33279800415

    #mosql.util.delimit_identifier = None
    #print timeit(lambda: select('person', {'name': 'Mosky Liu'}, ('person_id', 'name'), limit=10, order_by='person_id'))
    ## -> 3.94950485229

    ##from mosql.common import select as old_select

    ##print timeit(lambda: old_select('person', {'name': 'Mosky Liu'}, ('person_id', 'name'), limit=10, order_by='person_id'))
    ### -> 6.79131507874
