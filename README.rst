The full version of this documentation is at `mosql.mosky.tw
<http://mosql.mosky.tw>`_.

MoSQL --- More than SQL
=======================

It lets you use the common Python's data structures to build SQLs, and provides
a convenient model of result set.

The main features:

1. Easy-to-learn --- Everything is just plain data structure or SQL keyword. See
   `The SQL Builders`_.
2. Convenient    --- It makes result set more easy to use. See `The Model of
   Result Set`_.
3. Secure        --- It prevents the SQL injection from both identifier and
   value.
4. Faster        --- It just builds the SQLs from Python's data structure and
   then send to the connector.

It is just "More than SQL".

NOTE: The versions after v0.2 are a new branch and it does **not** provide
backward-compatibility for v0.1.x.

The SQL Builders
----------------

::

    >>> from mosql import build
    >>> build.select('author', {'email like': '%mosky%@%'})
    SELECT * FROM "author" WHERE "email" LIKE '%mosky%@%'

It is very easy to build a query by Python's data structures and
`mosql.build <http://mosql.mosky.tw/builders.html#module-mosql.build>`_.

There is more explanation of the builders --- `mosql.build
<http://mosql.mosky.tw/builders.html#module-mosql.build>`_.

It also provides `mosql.result.Model
<http://mosql.mosky.tw/result.html#mosql.result.Model>`_ for result set, and you
can use the same way to make queries to database.

The Model of Result Set
-----------------------

Here is a SQL and the result set:

::

    mosky=> select * from detail where person_id in ('mosky', 'andy') order by person_id, key;
     detail_id | person_id |   key   |           val            
    -----------+-----------+---------+--------------------------
             5 | andy      | email   | andy@gmail.com
             3 | mosky     | address | It is my first address.
             4 | mosky     | address | It is my second address.
             1 | mosky     | email   | mosky.tw@gmail.com
             2 | mosky     | email   | mosky.liu@pinkoi.com
            10 | mosky     | email   | mosky@ubuntu-tw.org
    (6 rows)

Then, use the model configured (the module, ``detail``, is in the `examples
<https://github.com/moskytw/mosql/tree/dev/examples>`_) to do so:

::

    >>> from detail import Detail
    >>> for detail in Detail.arrange({'person_id': ('mosky', 'andy')}):
    ...     print detail
    ... 
    {'detail_id': [5],
     'key': 'email',
     'person_id': 'andy',
     'val': ['andy@gmail.com']}
    {'detail_id': [3, 4],
     'key': 'address',
     'person_id': 'mosky',
     'val': ['It is my first address.', 'It is my second address.']}
    {'detail_id': [1, 2, 10],
     'key': 'email',
     'person_id': 'mosky',
     'val': ['mosky.tw@gmail.com', 'mosky.liu@pinkoi.com', 'mosky@ubuntu-tw.org']}


Here I use `arrange
<http://mosql.mosky.tw/result.html#mosql.result.Model.arrange>`_ for taking
advantages from the model configured, so the result sets are grouped into three
model instances, but the plain methods, such as `select
<http://mosql.mosky.tw/result.html#mosql.result.Model.select>`_, are also
available.

It converts the each result set into column-oriented model. The columns are
squashable. The non-list values above are just the squashed columns. See
`mosql.result <http://mosql.mosky.tw/result.html#module-mosql.result>`_ for more
information.

There is more explanation of the model --- `mosql.result <http://mosql.mosky.tw/result.html#module-mosql.result>`_.

Installation
------------

It is easy to install MoSQL with pip:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git
