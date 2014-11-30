#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
.. deprecated:: 0.6
    The :mod:`mosql.result` will be removed in a future release, so this module
    will not be needed once :mod:`~mosql.result` is removed.

.. warning::
    This module will be removed in version 0.11.

An alternative of built-in `json`.

It is compatible with :py:mod:`mosql.result` and built-in `datetime`.

.. versionadded:: 0.2
    It supports the new :mod:`mosql.result`.

.. versionadded:: 0.1.1
'''

# --- the removal warning ---
from .util import warning
warning('mosql.json will be removed in version 0.11.')
# --- end ---

__all__ = ['dump', 'dumps', 'load', 'loads', 'ModelJSONEncoder']

import imp

try:
    # it imports module from built-in first, so it skipped this json.py
    json = imp.load_module('json', *imp.find_module('json'))
except ImportError:
    import simplejson as json

from datetime import datetime, date
from functools import partial

from .result import Model, ColProxy, RowProxy

class ModelJSONEncoder(json.JSONEncoder):
    '''It is compatible with :py:mod:`mosql.result` and built-in `datetime`.'''

    def default(self, obj):

        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError, e:
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, Model):
                return dict(obj)
            elif isinstance(obj, ColProxy):
                return list(obj)
            elif isinstance(obj, RowProxy):
                return dict(obj)
            else:
                raise e

dump = partial(json.dump, cls=ModelJSONEncoder)
'''It uses the :py:class:`ModelJSONEncoder`.'''

dumps = partial(json.dumps, cls=ModelJSONEncoder)
'''It uses the :py:class:`ModelJSONEncoder`.'''

load = json.load
'''It is same as `json.load`.'''

loads = json.loads
'''It is same as `json.loads`.'''
