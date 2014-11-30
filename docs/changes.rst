The Change Log
==============

v0.10
-----

The Security-related Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. The standard :func:`~mosql.util.escape` and
   :func:`~mosql.util.escape_identifier` raises :exc:`ValueError` if the string
   has a null byte now. The null byte may truncate SQL, but it still depends on
   how database handls it. Thanks `Orange <http://blog.orange.tw>`_ for
   reporting this issue.
#. Removed the support to use subquery directly. Use the new
   :func:`~mosql.util.subq` instead.

As far as we know, the two weaknesses can't be exploited, but we still strongly
recommend you to upgrade to this version.

The Majoy Changes
~~~~~~~~~~~~~~~~~

#. The :class:`~mosql.db.Database` supports to keep connection open.
#. The :class:`~mosql.db.Database` is thread-safe now.
#. The :func:`~mosql.query.insert` supports multi-value.
#. The :func:`~mosql.util.build_where` translates ``x IN ()`` into simple
   ``FALSE``.
#. The :func:`~mosql.util.build_where` allows to use `pair` as key to include
   operator.
#. The :class:`mosql.util.Statement.format` ignores false clause argument in
   bool context.
#. The :class:`mosql.util.Statement.format` raises :exc:`TypeError` if there is
   any unused clause argument.
#. Added :meth:`mosql.util.Query.enable_echo` to echo the SQL it builds.

You can find most of the examples in :func:`~mosql.query.select`.

The Minor Changes
~~~~~~~~~~~~~~~~~

#. Added :func:`~mosql.util.dot`, :func:`~mosql.util.as_`,
   :func:`~mosql.util.asc`, :func:`~mosql.util.desc`, :func:`~mosql.util.subq`,
   and :func:`~mosql.util.in_operand`.
#. All of the patch modules in :doc:`/patches` have a ``.patch()`` method to
   apply the patch again.
#. The :func:`~mosql.util.identifier` was split into
   :func:`~mosql.util.identifier`, :func:`~mosql.util.identifier_as`, and
   :func:`~mosql.util.identifier_dir`.
#. The :func:`~mosql.util.identifier` supports to use `pair` to include table
   and column name; and
#. The :func:`~mosql.util.identifier_as` and :func:`~mosql.util.identifier_dir`
   also supports to use `pair` to include alias or direction.
#. Renamed :exc:`~mosql.util.OptionError` to :exc:`~mosql.util.DirectionError`.
#. The :func:`~mosql.util.delimit_identifier`,
   :data:`~mosql.util.allowed_operators`, and
   :data:`~mosql.util.allowed_directions` don't allow to disable anymore. Use
   :class:`~mosql.util.raw` instead.

Misc.
~~~~~

#. The deprecated modules in :doc:`/depreacted` will be removed in 0.11.
#. Refined all the documentation.

v0.9.1
------

1. Now :func:`~mosql.util.qualifier` supports to encode ``unicode`` into utf-8
   ``str`` automatically.

v0.9
----

1. Added MySQL-specific ``UPDATE FOR`` and ``LOCK IN SHARE MODE`` for
   :func:`~mosql.query.select`.
2. Added PostgreSQL-specific ``FOR``, ``OF`` and ``NOWAIT`` for
   :func:`~mosql.query.select`.
3. Fixed select can't use ``from_`` as argument.
4. Added and changed the arguments of :class:`~mosql.util.Clause`.

v0.8.1
------

1. Fixed the regression that causes converting int fails. `#33
   <https://github.com/moskytw/mosql/issues/33>`_

v0.8
----

1. ``columns`` now is the alias of ``select``.
2. Fixed the complain of inserting with empty dict.
3. Added :mod:`mosql.sqlite` for better SQLite support.
4. Added :func:`mosql.query.replace`.
5. Renamed :mod:`mosql.statement` to :mod:`mosql.stmt`.
6. Added :mod:`mosql.func` for basic SQL functions supprt.
7. Support using pair (2-tuple) to build ``AS`` statement.
8. Support subquery perfectly.

Thanks `Tzu-ping Chung (uranusjr) <https://github.com/uranusjr>`_ contributed
the PRs (`#27 <https://github.com/moskytw/mosql/pull/27>`_,  `#15
<https://github.com/moskytw/mosql/pull/15>`_, `#14
<https://github.com/moskytw/mosql/pull/14>`_, and `#12
<https://github.com/moskytw/mosql/pull/12>`_) which bring the improvement 2, 6,
7 and 8.

Thanks `lucemia <https://github.com/lucemia>`_ contributed the PRs (`#19
<https://github.com/moskytw/mosql/pull/19>`_, `#13
<https://github.com/moskytw/mosql/pull/13>`_) which bring the improvement 3 and
4.

And, thanks `PyCon TW <http://pycon.tw>`_ and your `sprint event
<https://kktix.com/events/9691cb>`_ in 2013 Oct! :)

v0.7.4
------

1. Fixed the compatibility of :mod:`mosql.db` with Python 2.6. Thanks `Aminzai
   <http://github.com/moskytw/mosql/pull/23>`_.

v0.7.3
------

1. Added :func:`mosql.util.and_`.

v0.7.2
------

1. :func:`mosql.util.or_` should add paren.

v0.7.1
------

1. Improved the compatibility with MySQLdb.

v0.7
----

1. Added the Travis CI badge. Thanks for the contribution from `xKerman
   <https://github.com/moskytw/mosql/pull/7>`_.
2. Added :doc:`/db`.
3. Arranged the `examples
   <https://github.com/moskytw/mosql/tree/dev/examples>`_.

v0.6.1
------

1. Nothing but the change of the docs.

v0.6
----

.. note::
    Some of the modules are deprecated after v0.6, check :doc:`/deprecated` for
    more information.

1. Deprecated some of the modules. Check :doc:`/deprecated` for detail.
2. Made the :class:`mosql.util.Clause` and :class:`mosql.util.Statement` better.
3. Added the :class:`mosql.util.Query`.
4. Added the :mod:`mosql.query`, :mod:`mosql.statement`, :mod:`mosql.clause`,
   and :mod:`mosql.chain` for the instances in common use.

v0.5.3
------

1. Fixed the compatibility of :mod:`mosql.util` with types which inherit the
   basic types.

v0.5.2
------

1. Fixed the compatibility of :mod:`mosql.json` with
   :class:`mosql.result.Model`.

v0.5.1
------

1. The :meth:`mosql.result.Model.save` uses
   :attr:`mosql.result.Model.arrange_by` to save the changes on column squashed.
2. The :meth:`mosql.result.Model.clear` is also improved.
3. Improved the program of loading result set.
4. The :meth:`mosql.result.Model.select` or :meth:`mosql.result.Model.where`
   returns None if no row is returned.

v0.5
----

1. Improved the code of :class:`mosql.result.Model`.
2. Added :meth:`mosql.result.Model.new`.
3. Added :meth:`mosql.result.Model.add`.
4. Added :meth:`mosql.result.Model.clear`.
5. The :meth:`mosql.result.Model.perform` now supports to call procedure,
   execute SQL with parameter and `executemany`.
6. Fixed the compatibility with MySQL.

v0.4
----

1. Improved the code of :class:`mosql.result.Model`.
2. Added :attr:`mosql.result.Model.squash_all` for 1:1 table.
3. Added :meth:`mosql.result.Model.rows` for iterating the rows.
4. The rows in :class:`mosql.result.Model` can be accessed by row index now.
5. Added :meth:`mosql.result.Model.getcur` for customizing cursor.
6. The :meth:`mosql.result.Model.pop` returns the row it poped now.
7. The :meth:`mosql.result.Model.row` and :meth:`mosql.result.Model.col` are removed.

v0.3
----

1. Improved memory usage of :meth:`mosql.result.Model.arrange`.
2. MoSQL supports to use native escape functions now (via :mod:`mosql.psycopg2_escape` or :mod:`mosql.MySQLdb_escape`).

v0.2.1
------

1. Fixed a bug of :meth:`mosql.result.Model.append`.

v0.2
----

.. note::
    The versions after v0.2 are a new branch and it does **not** provide
    backward-compatibility for v0.1.x.

1. The :mod:`mosql.result` is totally rewritten, and does **not** provide the
   backward-compatibility. See the doc for more info.
2. The :mod:`mosql.common` is renamed as :mod:`mosql.build`.
3. The :mod:`mosql.ext` is removed.
4. The :func:`mosql.build.insert` uses `set` instead of `pairs_or_columns`.
5. The :func:`mosql.build.insert` supports "on duplicate key update" now.
6. The :mod:`mosql.select` uses `*` if user pass ``None`` in.
7. MoSQL passed all of the injection tests from `sqlmap <http://sqlmap.org/>`_
   on value and identifier with PostgreSQL and MySQL.

v0.1.6
------

1. The :mod:`mosql.util` is faster (1.35x~1.7x) after rewriting.
2. The :mod:`mosql.util` also supports to delimit the identifier (for avoiding
   injection from identifier),
3. use arbitrary SQL statements by :class:`mosql.util.raw`,
4. and customize parameter name of prepared statement by
   :class:`mosql.util.param` now.
5. The :mod:`mosql.ext` is deprecated now, please use :mod:`mosql.common`
   instead.

v0.1.5
------

1. This version refined the :py:mod:`mosql.mysql`.
2. MoSQL with PostgreSQL or MySQL passed all of the injection tests from `sqlmap
   <http://sqlmap.org/>`_.

v0.1.4
------

1. Fixed the dumped value of datetime, date and time.

v0.1.3
------

1. This version reverted the #3 changes in the previous version.
2. By default, the :class:`mosql.result.Model` now orders the result set by
   nothing.

v0.1.2
------

1. Added the :py:mod:`mosql.mysql`.
2. The :py:meth:`mosql.result.Model.seek` now respects the arguments from users.
3. The :py:attr:`~mosql.result.Model.group_by` now uses the value of
   :py:attr:`~mosql.result.Model.identify_by`, by default.
4. The :py:attr:`~mosql.result.Model.order_by` stops using the value of
   :py:attr:`~mosql.result.Model.identify_by`.

v0.1.1
------

1. Added the :py:mod:`mosql.json`.
2. Added the :py:meth:`mosql.result.Model.customize`.
3. The :py:class:`~mosql.result.Model` now can use attributes to access data.
4. The :py:class:`~mosql.result.Model` now allows user to customize insert,
   select, update and delete.
5. It respects the ``column_names`` when do a select.
6. Fixed the wrong sql without specifying ``identify_by``.
7. Fixed the SQL dumped with None. (issue `#1
   <https://github.com/moskytw/mosql/issues/1>`_)
