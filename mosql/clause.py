#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides common clauses.'''

from .util import Clause, star
from .chain import identifier_as_list, where_list
from .chain import single_identifier, column_list, values_list, set_list
from .chain import statement_list, identifier_list, identifier_dir_list, single_value
from .chain import single_identifier_as, on_list

# common clauses
returning = Clause('returning' , identifier_as_list)
where     = Clause('where'     , where_list)

# for insert statement
insert    = Clause('insert into', single_identifier, alias='table')
columns   = Clause('columns'    , column_list, hidden=True)
values    = Clause('values'     , values_list)
on_duplicate_key_update = Clause('on duplicate key update', set_list)

# for select statement
select   = Clause('select'  , identifier_as_list, default=star, alias='columns')
from_    = Clause('from'    , identifier_as_list, alias='table')
joins    = Clause('joins'   , statement_list, hidden=True)
group_by = Clause('group by', identifier_list)
having   = Clause('having'  , where_list)
order_by = Clause('order by', identifier_dir_list)
limit    = Clause('limit'   , single_value)
offset   = Clause('offset'  , single_value)

# for PostgreSQL-specific select
for_   = Clause('for')
of     = Clause('of'    , identifier_list)
nowait = Clause('nowait', no_argument=True)

# for MySQL-specific select
for_update = Clause('for update', no_argument=True)
lock_in_share_mode = Clause('lock in share mode', no_argument=True)

# for update statement
update = Clause('update', single_identifier_as, alias='table')
set_   = Clause('set'   , set_list)

# for delete statement
delete = Clause('delete from', single_identifier_as, alias='table')

# for join statement
join  = Clause('join' , single_identifier_as, alias='table')
type_ = Clause('type' , hidden=True)
on    = Clause('on'   , on_list)
using = Clause('using', column_list)

# for replace statement
replace = Clause('replace into', single_identifier, alias='table')
