#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides various database-specific syntax patches.
'''

__all__ = ['EnginePatcher', 'mysql', 'sqlite']

import mosql.util
from . import _mysql, _sqlite

class EnginePatcher(object):
    '''This class implements the context manager interface for syntax patching.

    :param patches: a mapping of members to be patched
    :type patches: `dict`
    '''
    def __init__(self, patches):
        self._backup = {}
        self._patches = patches

    def __enter__(self):
        for k in self._patches:
            self._backup[k] = getattr(mosql.util, k)
            setattr(mosql.util, k, self._patches[k])
        return self._backup

    def __exit__(self, exc_type, exc_val, exc_tb):
        while self._backup:
            k, v = self._backup.popitem()
            setattr(mosql.util, k, v)

def mysql():
    '''This context manager applies MySQL syntax for :mod:`mosql.util` temporarily.

    >>> with mysql():
    ...     print select('person', {'person_id': 'mosky'})
    ...
    SELECT * FROM `person` WHERE `person_id` = 'mosky'
    >>> print select('person', {'person_id': 'mosky'})
    SELECT * FROM "person" WHERE "person_id" = 'mosky'
    '''
    patches = {
        'escape': _mysql.fast_escape,
        'format_param': _mysql.format_param,
        'delimit_identifier': _mysql.delimit_identifier,
        'escape_identifier': _mysql.escape_identifier
    }
    return EnginePatcher(patches)

mysql.load = mysql().__enter__
'''This function applies MySQL syntax for :mod:`mosql.util` perminantely.

Usage::

    from mosql.patch import mysql
    mysql.load()

:returns: Names and function instances that were replaced in :mod:`mosql.util`
:rtype: `dict`
'''

def sqlite():
    '''This context manager applies SQLite syntax for :mod:`mosql.util` temporarily.

    >>> with sqlite():
    ...     print select('person', {'person_id': param('person_id')})
    SELECT * FROM "person" WHERE "person_id" = :person_id
    >>> print select('person', {'person_id': param('person_id')})
    SELECT * FROM "person" WHERE "person_id" = %(person_id)s
    '''
    return EnginePatcher({'format_param': _sqlite.format_param})

sqlite.load = sqlite().__enter__
'''This function applies SQLite syntax for :mod:`mosql.util` perminantely.

Usage::

    from mosql.patch import mysql
    mysql.load()

:returns: Names and function instances that were replaced in :mod:`mosql.util`
:rtype: `dict`
'''
