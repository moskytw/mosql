The full version of this documentation is at `mosql.mosky.tw <http://mosql.mosky.tw>`_.

MoSQL --- More than SQL
=======================

MoSQL is a lightweight Python library which assists programmer to use SQL.

It is designed to take the high performance from using pure SQL, and just do the necessary abstracting of SQL.

It has two major parts:

The first part is SQL builders which help you to build SQL with common Python data types:

::

    >>> from mosql.common import select
    >>> select('person', {'age >': 18})
    'SELECT * FROM person WHERE age > 18'

It converts the Python data types to SQL statements. You can find more exmaples in `mosql.common <http://mosql.mosky.tw/builders.html#module-mosql.common>`_.

The second part is a easy-to-use interface of the result set. For an instance, we assume there is a table like this:

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

After setuped the `mosql.result.Model <http://mosql.mosky.tw/result.html#mosql.result.Model>`_, it will be a proxy to access your result set, and provide a nice interface to modify the rows:

::

    >>> from my_models import Detail
    >>> for detail in Detail.find(person_id='mosky')):
    ...     print detail
    {'person_id': 'mosky', 'detail_id': [3, 4], 'val': ['address', '...'], 'key': 'address'}
    {'person_id': 'mosky', 'detail_id': [1, 6, 10], 'val': ['email', '...', '...'], 'key': 'email'}

For simplicity, the Model, which is a *dict-like* object, is rendered as the dict, and the `mosql.result.Column`, which is a *list-like* object, is rendered as the list. The Model is a *grouped* result set, and the Columns are the *proxies* for a Model. Any operation on the Columns will be redirect to a Model.

`Start with MoSQL’s model <http://mosql.mosky.tw/result.html#tutorial-of-model>`_ describes more details about how to use the `Model`.

Installation
------------

It is easy to install MoSQL with `pip`:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git
