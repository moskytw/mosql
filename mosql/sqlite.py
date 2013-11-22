#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides tools to apply SQLite-specific stuffs to :mod:`mosql.util`.
'''

import contextlib
import mosql.util

def format_param(s=''):
    # TODO: This function leaks doc.
    return ':%s' % s if s else '?'

def load():
    backups = {'format_param': mosql.util.format_param}
    mosql.util.format_param = format_param
    return backups

@contextlib.contextmanager
def apply():
    backups = load()
    yield
    mosql.util.format_param = backups['format_param']

if __name__ == '__main__':
    import doctest
    doctest.testmod()
