#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .util2 import *

# defines formatting chains
single_value      = (value, )
single_identifier = (identifier, )
identifier_list   = (identifier, concat_by_comma)
where_list        = (build_where, )
set_list          = (build_set, )
statement_list    = (concat_by_space, )

# insert

insert  = Clause('insert into', single_identifier)
columns = Clause('columns'    , (identifier, concat_by_comma, paren), hidden=True)
values  = Clause('values'     , (value, concat_by_comma, paren))
returning = Clause('returning'  , identifier_list)

insert_into_stat = Statement([insert, columns, values, returning])

def insert(table, pairs_or_columns=None, values=None, **clauses_args):

    clauses_args['insert into'] = table

    if values is None:
        if hasattr(pairs_or_columns, 'items'):
            pairs = pairs_or_columns.items()
        else:
            pairs = pairs_or_columns
        clauses_args['columns'], clauses_args['values'] = zip(*pairs)
    else:
        clauses_args['columns'] = pairs_or_columns
        clauses_args['values']  = values

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

def select(table, where=None, select=raw('*'), **clauses_args):

    clauses_args['from']   = table
    clauses_args['where']  = where
    clauses_args['select'] = select

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

def update(table, where, set, **clauses_args):

    clauses_args['update'] = table
    clauses_args['where']  = where
    clauses_args['set']    = set

    return update_stat.format(clauses_args)

# delete from

delete = Clause('delete from', single_identifier)

delete_stat = Statement([delete, where, returning])

def delete(table, where, **clauses_args):

    clauses_args['delete from'] = table
    clauses_args['where'] = where

    return delete_stat.format(clauses_args)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    print insert('person', {'person_id': 'daniel', 'name': 'Daniel Boulud'})
    print select('person', {'name like': '%mosky%'}, limit=3, order_by=('a', 'b'))
    print update('person', {'person_id': 'mosky'}, {'name': 'Mosky Liu'})
    print delete('person', {'person_id': 'daniel'})
