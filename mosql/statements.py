#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .util import Statement
from .clauses import returning, where
from .clauses import insert, columns, values, on_duplicate_key_update
from .clauses import select, from_, joins, group_by, having, order_by, limit, offset
from .clauses import update, set_
from .clauses import delete
from .clauses import type_, join, on, using

def insert_preprocessor(clause_args):

    if 'values' not in clause_args and \
       'set' in clause_args        and \
       hasattr(clause_args['set'], 'items'):

        clause_args['columns'], clause_args['values'] = zip(*clause_args['set'].items())

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
