The Module Deprecated after v0.6
================================

After v0.6, the following modules are deprecated and they will be obsoleted in a
future release:

1. :mod:`mosql.build`
2. :mod:`mosql.result`
3. :mod:`mosql.json`
4. :mod:`mosql.psycopg2_escape`
5. :mod:`mosql.MySQLdb_escape`

.. testsetup::

    from mosql.util import *
    from mosql.build import *
    from mosql.result import *
    from mosql.json import *

The Common SQL Builders --- :py:mod:`mosql.build`
-------------------------------------------------

.. automodule:: mosql.build
    :members:

The Model of Result Set --- :py:mod:`moqsl.result`
--------------------------------------------------

.. automodule:: mosql.result
    :members:

The Compatible JSON Encoder and Decoder --- :py:mod:`mosql.json`
----------------------------------------------------------------

.. automodule:: mosql.json
    :members:

The Native Escape Functions of Psycopg2 --- :py:mod:`moqsl.psycopg2_escape`
---------------------------------------------------------------------------

.. automodule:: mosql.psycopg2_escape
    :members:

The Native Escape Function of MySQLdb --- :py:mod:`moqsl.MySQLdb_escape`
------------------------------------------------------------------------

.. automodule:: mosql.MySQLdb_escape
    :members:
