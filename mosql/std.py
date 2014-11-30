#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applies the standard functions to :mod:`mosql.util`.

The usage:

::

    import mosql.std

If you want to patch again:

::

    mosql.std.patch()

It will replace the functions in :mod:`mosql.util` with original standard functions.

.. versionadded:: 0.10
'''

import mosql.util

def patch():
    '''Applies the standard functions again.'''
    mosql.util.escape = mosql.util.std_escape
    mosql.util.format_param = mosql.util.std_format_param
    mosql.util.delimit_identifier = mosql.util.std_delimit_identifier
    mosql.util.stringify_bool = mosql.util.std_stringify_bool
    mosql.util.escape_identifier = mosql.util.std_escape_identifier

patch() # patch it when load this module
