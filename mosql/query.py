#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides common queies.'''

from .util import Query
from .statement import insert, select, update, delete, join

insert = Query(insert, ('table', 'set'))
select = Query(select, ('table', 'where'))
update = Query(update, ('table', 'where', 'set'))
delete = Query(delete, ('table', 'where'))

join       = Query(join, ('table', 'on'))
left_join  = join.breed({'type': 'left'})
right_join = join.breed({'type': 'right'})
cross_join = join.breed({'type': 'cross'})
