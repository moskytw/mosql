#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

def select_preprocessor(clause_args):

    clause_args.setdefault('select', star)

    if 'table' in clause_args:
        clause_args['select'] = clause_args['table']

    if 'order_by' in clause_args:
        clause_args['order by'] = clause_args['order_by']

    if 'group_by' in clause_args:
        clause_args['group by'] = clause_args['group_by']

select = Query(select_stat, select_preprocessor)
print select.stringify(table='order', where={'order_id': 123})

order_select = select.breed({'table': 'order', 'order by': 'order_created'})
print order_select(where={'order_id': 123})
