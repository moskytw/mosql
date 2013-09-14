.. sql-helper documentation master file, created by
   sphinx-quickstart on Thu Feb 14 22:47:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoSQL --- More than SQL
=======================

It lets you use the common Python's data structures to build SQLs. Here are the
main features:

1. Easy-to-learn --- Everything is just plain data structure or SQL keyword.
2. Flexible --- The queries it builds fully depends on the structure you provide.
3. Secure --- It prevents the SQL injection from both identifier and value.
4. Fast --- It just builds the SQLs from Python's data structures.

It is just more than SQL.

.. note::
    Some of the modules are deprecated after v0.6, check :doc:`/deprecated` for
    more information.

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

MoSQL is Elegent
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

How about to send it to db directly? Yes, it is in the to-do, but not for now.

.. seealso::

    You can check :doc:`/query` for the detail usage, or there are also many
    `examples <https://github.com/moskytw/mosql/tree/dev/examples>`_ which
    really interact with database.

Like it?
--------

It is easy to install MoSQL with pip:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git

Read More
=========

.. toctree::
    :maxdepth: 1

    query
    util
    mysql
    deprecated
    changes

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
