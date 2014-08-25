.. sql-helper documentation master file, created by
   sphinx-quickstart on Thu Feb 14 22:47:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoSQL --- More than SQL
=======================

.. .. image:: https://travis-ci.org/moskytw/mosql.png
..    :target: https://travis-ci.org/moskytw/mosql
.. 
.. .. image:: https://pypip.in/v/mosql/badge.png
..    :target: https://pypi.python.org/pypi/mosql
.. 
.. .. image:: https://pypip.in/d/mosql/badge.png
..    :target: https://pypi.python.org/pypi/mosql

It lets you use the common Python's data structures to build SQLs.

It is the slide of the talk, "MoSQL: More than SQL, but Less than ORM", at
`PyCon APAC 2013 <http://apac-2013.pycon.jp/>`_. It introduces MoSQL after v0.6.

.. raw:: html

    <div style="width: 400px">
        <script async class="speakerdeck-embed" data-id="1de8b4600b45013184c80a56b6e9c79b" data-ratio="1.33333333333333" src="//speakerdeck.com/assets/embed.js"></script>
    </div>

The main features:

1. Easy-to-learn --- Everything is just plain data structure or SQL keyword.
2. Flexible --- The queries it builds fully depends on the structure you provide.
3. Secure --- It prevents the SQL injection from both identifier and value.
4. Fast --- It just builds the SQLs from Python's data structures.

It is just more than SQL.

.. raw:: html

    <div id="fb-root"></div>
    <script>(function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "//connect.facebook.net/zh_TW/all.js#xfbml=1";
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));</script>


    <style>
    #social-btns div {
        float: left;
    }
    #social-btns:after {
        content: ".";
        display: block;
        font-size: 0;
        clear: both;
    }
    </style>

    <div id='social-btns'>
        <div>
            <iframe src="http://ghbtns.com/github-btn.html?user=moskytw&repo=mosql&type=watch&count=true" allowtransparency="true" frameborder="0" scrolling="0" width="85" height="20"></iframe>
        </div>

        <div>
            <div class="fb-like" data-href="http://mosql.mosky.tw" data-send="true" data-layout="button_count" data-width="450" data-show-faces="true"></div>
        </div>
    </div>

MoSQL is Elegant
----------------

Here we have a dictionary which includes the information of a person:

>>> mosky = {
...    'person_id': 'mosky',
...    'name'     : 'Mosky Liu',
... }

And we want to insert it into a table named person. It is easy with
:mod:`mosql.query`.

>>> from mosql.query import insert
>>> print insert('person', mosky)
INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

.. seealso::

    You can check :doc:`/query` for the detail usage, or there are also many
    `examples <https://github.com/moskytw/mosql/tree/dev/examples>`_ which
    really interact with database.

Like it?
--------

It is available on PyPI:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git

Read More
=========

.. toctree::
    :maxdepth: 2

    query
    util
    db
    patches

and here is :doc:`/changes`.

.. note::
    Some of the modules are deprecated after v0.6, check :doc:`/deprecated` for
    more information.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
