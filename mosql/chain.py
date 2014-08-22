#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides common formatting chain.'''

from .util import value, identifier, identifier_as, identifier_dir, paren
from .util import concat_by_comma, concat_by_space, build_values_list, build_where, build_set, build_on

single_value         = (value, )
single_identifier    = (identifier, )
single_identifier_as = (identifier_as, )
identifier_list      = (identifier, concat_by_comma)
identifier_as_list   = (identifier_as, concat_by_comma)
identifier_dir_list  = (identifier_dir, concat_by_comma)
column_list          = (identifier, concat_by_comma, paren)
values_list          = (build_values_list, )
where_list           = (build_where, )
set_list             = (build_set, )
on_list              = (build_on, )
statement_list       = (concat_by_space, )
