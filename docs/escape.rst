The Native Escape Functions
===========================

If you don't use utf-8 for your connection, you need to use the native escape
function for security.

But it is still better to change your connection encoding to utf-8 rather than
use it, because the native escape function only works for value, so attacker
can inject malicious code in the identifiers.

.. seealso ::

    The base.py in `examples
    <https://github.com/moskytw/mosql/tree/dev/examples>`_ shows how to ensure
    the security by changing your connection encoding.

Psycopg2 --- :py:mod:`moqsl.psycopg2_escape`
--------------------------------------------

.. automodule:: mosql.psycopg2_escape
    :members:

MySQLdb --- :py:mod:`moqsl.MySQLdb_escape`
------------------------------------------

.. automodule:: mosql.MySQLdb_escape
    :members:
