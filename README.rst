MoSQL --- More than SQL
=======================

MoSQL is a lightweight Python library which assists programmer to use SQL.

It has two major parts:

The first part is SQL builders which help you to build SQL with common Python data types:

::

    >>> from mosql.common import select
    >>> select('person', {'age >': 18})
    'SELECT * FROM person WHERE age > 18'

It converts the Python data types to SQL statements. You can find more exmaples in `mosql.common <http://mosql.mosky.tw/builders.html#module-mosql.common>`_.

The second part is a easy-to-use interface of the result set. We assume there is a table like this:

::

    db=> select * from detail where person_id='mosky';
     detail_id | person_id |   key   |   val            
    -----------+-----------+---------+---------
             4 | mosky     | address | address
             3 | mosky     | address | ...
            10 | mosky     | email   | email
             6 | mosky     | email   | ...
             1 | mosky     | email   | ...
    (5 rows)

After setuped the `mosql.result.Model`, it is more easy to access this table:

::

    >>> from my_models import Detail
    >>> for detail in Detail.find(person_id='mosky')):
    ...     print detail
    {'person_id': 'mosky', 'detail_id': [3, 4], 'val': ['address', '...'], 'key': 'address'}
    {'person_id': 'mosky', 'detail_id': [1, 6, 10], 'val': ['email', '...', '...'], 'key': 'email'}

For simplicity, the `mosql.result.Model` is rendered as a dict, and the lists in the :`mosql.result.Model` are not simple lists, too. They are `mosql.result.Column` which act as a proxy. It will redirect your operations on it to the `mosql.result.Model` which it belongs to.

`Start with MoSQL’s model <http://mosql.mosky.tw/result.html#tutorial-of-model>`_ describes more details about how to use`mosql.result.Model`.

Installation
------------

It is easy to install MoSQL with `pip`:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git

You can find the full documentation at `mosql.mosky.tw <http://mosql.mosky.tw>`_.
