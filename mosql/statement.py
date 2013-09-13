#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides common statements.'''

from .util import Statement
from .clause import returning, where
from .clause import insert, columns, values, on_duplicate_key_update
from .clause import select, from_, joins, group_by, having, order_by, limit, offset
from .clause import update, set_
from .clause import delete
from .clause import type_, join, on, using

def insert_preprocessor(clause_args):

    if 'values' not in clause_args and 'set' in clause_args:

        if hasattr(clause_args['set'], 'items'):
            pairs = clause_args['set'].items()
        else:
            pairs = clause_args['set']

        clause_args['columns'], clause_args['values'] = zip(*pairs)

insert = Statement([insert, columns, values, returning, on_duplicate_key_update], preprocessor=insert_preprocessor)
select = Statement([select, from_, joins, where, group_by, having, order_by, limit, offset])
update = Statement([update, set_, where, returning])
delete = Statement([delete, where, returning])

def join_preprocessor(clause_args):

    if 'type' not in clause_args:
        if 'using' in clause_args or 'on' in clause_args:
            clause_args['type'] = 'INNER'
        else:
            clause_args['type'] = 'NATURAL'
    else:
        clause_args['type'] = clause_args['type'].upper()

join = Statement([type_, join, on, using], preprocessor=join_preprocessor)
