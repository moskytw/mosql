.. image:: https://travis-ci.org/moskytw/mosql.png
   :target: https://travis-ci.org/moskytw/mosql

.. image:: https://pypip.in/v/mosql/badge.png
   :target: https://pypi.python.org/pypi/mosql

.. image:: https://pypip.in/d/mosql/badge.png
   :target: https://pypi.python.org/pypi/mosql

The full version of this documentation is at `mosql.mosky.tw
<http://mosql.mosky.tw>`_.

MoSQL --- More than SQL
=======================

It lets you use the common Python's data structures to build SQLs. Here are the
main features:

1. Easy-to-learn --- Everything is just plain data structure or SQL keyword.
2. Flexible --- The query it builds fully depends on the structure you provide.
3. Secure --- It prevents the SQL injection from both identifier and value.
4. Fast --- It just translates Python data structure into SQL.

It is just more than SQL.

Some of the modules are deprecated after v0.6, check `The Modules Deprecated
after v0.6 <http://mosql.mosky.tw/deprecated.html>`_ for more information.

MoSQL is Elegant
----------------

Here we have a dictionary which includes the information of a person:

>>> mosky = {
...    'person_id': 'mosky',
...    'name'     : 'Mosky Liu',
... }

And we want to insert it into a table named person. It is easy with `mosql.query
<http://mosql.mosky.tw/query.html#module-mosql.query>`_:

>>> from mosql.query import insert
>>> print insert('person', mosky)
INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

Check `The Common Queries — mosql.query <http://mosql.mosky.tw/query.html>`_ for
detail, or there are `examples
<https://github.com/moskytw/mosql/tree/dev/examples>`_ which interact with real
database.

Like it?
--------

It is available on PyPI:

::

    $ sudo pip install mosql

Or clone the source code from `GitHub <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git
