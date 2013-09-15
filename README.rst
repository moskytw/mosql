The full version of this documentation is at `mosql.mosky.tw
<http://mosql.mosky.tw>`_.

MoSQL --- More than SQL
=======================

It lets you use the common Python's data structures to build SQLs. Here are the
main features:

1. Easy-to-learn --- Everything is just plain data structure or SQL keyword.
2. Flexible --- The queries it builds fully depends on the structure you provide.
3. Secure --- It prevents the SQL injection from both identifier and value.
4. Fast --- It just builds the SQLs from Python's data structures.

It is just more than SQL.

Some of the modules are deprecated after v0.6, check `The Module Deprecated
after v0.6 <http://mosql.mosky.tw/deprecated.html>`_ for more information.

MoSQL is Elegent
----------------

Here we have a dictionary which includes the information of a person:

>>> mosky = {
...    'person_id': 'mosky',
...    'name'     : 'Mosky Liu',
... }

And we want to insert it into a table named person. It is easy with `mosql.query
<http://mosql.mosky.tw/query.html#module-mosql.query>`_.

>>> from mosql.query import insert
>>> print insert('person', mosky)
INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

How about to send it to db directly? Yes, it is in the to-do, but not for now.

You can check `The Common Queries — mosql.query
<http://mosql.mosky.tw/query.html>`_ for the detail usage, or there are also
many `examples <https://github.com/moskytw/mosql/tree/dev/examples>`_ which
really interact with database.

Like it?
--------

It is easy to install MoSQL with pip:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git
