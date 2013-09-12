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

select   = Clause('select'  , identifier_list, default=star)
from_    = Clause('from'    , identifier_list, alias='table')
joins    = Clause('joins'   , statement_list, hidden=True)
where    = Clause('where'   , where_list)
group_by = Clause('group by', identifier_list)
having   = Clause('having'  , where_list)
order_by = Clause('order by', identifier_list)
limit    = Clause('limit'   , single_value)
offset   = Clause('offset'  , single_value)

select_stat = Statement([select, from_, joins, where, group_by, having, order_by, limit, offset])

select = Query(select_stat)
print select.stringify(table='order', where={'order_id': 123})

order_select = select.breed({'table': 'order', 'order by': 'order_created'})
print order_select(where={'order_id': 123})
