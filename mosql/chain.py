#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides common formatting chain.'''

from .util import value, identifier, paren
from .util import concat_by_comma, concat_by_space, build_where, build_set, build_on

single_value      = (value, )
single_identifier = (identifier, )
identifier_list   = (identifier, concat_by_comma)
column_list       = (identifier, concat_by_comma, paren)
value_list        = (value, concat_by_comma, paren)
where_list        = (build_where, )
set_list          = (build_set, )
on_list           = (build_on, )
statement_list    = (concat_by_space, )

