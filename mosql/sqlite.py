#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applies the sqlite-specific stuff to :mod:`mosql.util`.

The usage:

::

    import mosql.sqlite

It will replace the functions in :mod:`mosql.util` with its functions.
'''

import mosql.patch
mosql.patch.sqlite.load()
