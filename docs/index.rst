.. sql-helper documentation master file, created by
   sphinx-quickstart on Thu Feb 14 22:47:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoSQL --- More than SQL
=======================

It lets you use the common Python's data structures to build SQLs.

.. The talk, "MoSQL: More than SQL, but Less than ORM", at PyCon TW 2013:
..
.. .. raw:: html
..
..     <div style="width: 600px">
..         <script async class="speakerdeck-embed"
..         data-id="5c9f3200a72b0130a3946ae3c3cecfe8" data-ratio="1.33507170795306"
..         src="//speakerdeck.com/assets/embed.js"></script>
..     </div>

The main features:

1. Easy-to-learn --- Everything is just plain data structure or SQL keyword.
2. Secure --- It prevents the SQL injection from both identifier and value.
3. Faster --- It just builds the SQLs from Python's data structure.

It is just "More than SQL".

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


Major Changes
-------------

After v0.6
~~~~~~~~~~

After this version, the following modules are deprecated and they will be obsoleted in a future release:

1. :mod:`mosql.build`
2. :mod:`mosql.result`
3. :mod:`mosql.json`
4. :mod:`mosql.psycopg2_escape`
5. :mod:`mosql.MySQLdb_escape`

If you are using them, those pages contain some advice for you.

After v0.2
~~~~~~~~~~

The versions after v0.2 are a new branch and it does **not** provide
backward-compatibility for v0.1.x.

Installation
------------

It is easy to install MoSQL with pip:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git

The Documentions
================

.. toctree::
    :maxdepth: 2

    changes.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
