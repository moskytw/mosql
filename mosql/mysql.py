#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applies the MySQL-specific stuff to :mod:`mosql.util`.

The usage:

::

    import mosql.mysql

It will replace the functions in :mod:`mosql.util` with its functions.
'''

import mosql.patch
mosql.patch.mysql.load()
