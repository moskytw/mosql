#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides common queries.'''

__all__ = [
    'insert', 'select', 'update', 'delete',
    'join', 'left_join', 'right_join', 'cross_join',
    'replace'
]

from .util import Query
from .stmt import insert, replace, select, update, delete, join

insert = Query(insert, ('table', 'set'))
select = Query(select, ('table', 'where'))
update = Query(update, ('table', 'where', 'set'))
delete = Query(delete, ('table', 'where'))

join       = Query(join, ('table', 'on'))
left_join  = join.breed({'type': 'left'})
right_join = join.breed({'type': 'right'})
cross_join = join.breed({'type': 'cross'})

replace = Query(replace, ('table', 'set'))
