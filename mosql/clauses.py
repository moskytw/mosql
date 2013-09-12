#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .util import star
from .util import value, identifier, paren, paren
from .util import concat_by_comma, concat_by_space, build_where, build_set, build_on
from .util import Clause

# the formatting chain
single_value      = (value, )
single_identifier = (identifier, )
identifier_list   = (identifier, concat_by_comma)
column_list       = (identifier, concat_by_comma, paren)
value_list        = (value, concat_by_comma, paren)
where_list        = (build_where, )
set_list          = (build_set, )
statement_list    = (concat_by_space, )

# common clauses
returning = Clause('returning'  , identifier_list)
where    = Clause('where'   , where_list)

# for insert statement
insert    = Clause('insert into', single_identifier, alias='table')
columns   = Clause('columns'    , column_list, hidden=True, alias='set')
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
on    = Clause('on'   , (build_on, ))
using = Clause('using', column_list)
