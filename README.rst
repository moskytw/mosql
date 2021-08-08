The full version of this documentation is at `mosql.mosky.tw
<http://mosql.mosky.tw>`_.

MoSQL --- More than SQL
=======================

It lets you use the common Python data structures to build SQLs. Here are the
main features:

1. Easy-to-learn --- Everything is just a plain Python object or SQL keyword.
2. Flexible --- The query it builds fully depends on the structure you provide.
3. Secure --- It prevents the SQL injection from both identifier and value.
4. Fast --- It simply translates the Python data structures into SQLs.

It is just more than SQL.

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
>>> print(insert('person', mosky))
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
