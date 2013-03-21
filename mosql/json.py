#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: the doc

import imp

try:
    # it imports module from built-in first, so it skipped this json.py
    json = imp.load_module('json', *imp.find_module('json'))
except ImportError:
    import simplejson as json

from datetime import datetime, date
from functools import partial

from .result import Model, Row, Column

class ModelJSONEncoder(json.JSONEncoder):

    def default(self, obj):

        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError, e:
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, Model):
                return dict(obj)
            elif isinstance(obj, Column):
                return list(obj)
            elif isinstance(obj, Row):
                return dict(obj)
            else:
                raise e

dump = partial(json.dump, cls=ModelJSONEncoder)
dumps = partial(json.dumps, cls=ModelJSONEncoder)
load = json.load
loads = json.loads
