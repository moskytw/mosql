#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides common clauses.'''

from .util import star, Clause
from .chain import identifier_list, where_list
from .chain import single_identifier, column_list, value_list, set_list
from .chain import statement_list, single_value
from .chain import on_list

# common clauses
returning = Clause('returning' , identifier_list)
where     = Clause('where'     , where_list)

# for insert statement
insert    = Clause('insert into', single_identifier, alias='table')
columns   = Clause('columns'    , column_list, hidden=True)
values    = Clause('values'     , value_list)
on_duplicate_key_update = Clause('on duplicate key update', set_list)

# for select statement
select   = Clause('select'  , identifier_list, default=star)
from_    = Clause('from'    , identifier_list, alias='table')
joins    = Clause('joins'   , statement_list, hidden=True)
group_by = Clause('group by', identifier_list)
having   = Clause('having'  , where_list)
order_by = Clause('order by', identifier_list)
limit    = Clause('limit'   , single_value)
offset   = Clause('offset'  , single_value)

# for update statement
update = Clause('update', single_identifier, alias='table')
set_   = Clause('set'   , set_list)

# for delete statement
delete = Clause('delete from', single_identifier, alias='table')

# for join statement
join  = Clause('join' , single_identifier, alias='table')
type_ = Clause('type' , tuple(), hidden=True)
on    = Clause('on'   , on_list)
using = Clause('using', column_list)
