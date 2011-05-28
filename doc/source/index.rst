.. contents::


Docuitils links
===============

- `Docutils Project Documentation Overview`_

  - `reStructuredText`_

    - `A ReStructuredText Primer`_
    - `Quick reStructuredText`_
    - `reStructuredText Cheat Sheet (text only)`_
    - `reStructuredText Demonstration`_
    - `reStructuredText Markup Specification`_
    - `reStructuredText Directives`_
    - `reStructuredText Interpreted Text Roles`_


.. _`Docutils Project Documentation Overview`:
   http://docutils.sourceforge.net/docs/

.. _`reStructuredText`:
   http://docutils.sourceforge.net/rst.html

.. _`A ReStructuredText Primer`:
   http://docutils.sourceforge.net/docs/user/rst/quickstart.html
.. _`Quick reStructuredText`:
   http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _`reStructuredText Cheat Sheet (text only)`:
   http://docutils.sourceforge.net/docs/user/rst/cheatsheet.txt
.. _`reStructuredText Demonstration`:
   http://docutils.sourceforge.net/docs/user/rst/demo.html
.. _`reStructuredText Markup Specification`:
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
.. _`reStructuredText Interpreted Text Roles`:
   http://docutils.sourceforge.net/docs/ref/rst/roles.html
.. _`reStructuredText Directives`:
   http://docutils.sourceforge.net/docs/ref/rst/directives.html


Special directives
==================


Show data in table - :rst:dir:`table-data`
------------------------------------------

.. rst:directive:: .. table-data:: path [path ...]

   Search data under the given list of `path` and show matched data and
   corresponding image(s).

   base : string (newlines removed)
       The base path for searching data. Real path to be used
       will be `{BASE}/{ARG}` where `{ARG}` is each value in
       the arguments and `{BASE}` is the value of this option.

   data : text [, text, ...]
       A comma- or space-separated list of the "dictionary path".
       For each path, period-separated path such as 'a.b.c' or
       'alpha.0.1' can be used.

   widths : integer [, integer...]
       A comma- or space-separated list of relative column widths.
       Note that the first column is data sub-table and the second and
       the after are the images specified in `:image:`.

   link : text [, text]
       A comma- or space-separated list of path to the link(s).
       Magic words ``%(path)s`` and ``%(relpath)s`` are available.

       ``%(path)s``
           This represents full path to the parent directory of the
           data file.
       ``%(relpath)s``
           This is the relative path of the ``%(path)s`` from the
           `base` directory.

   path-order : {'sort', 'sort_r'}
       Sort path or sort in the reversed order.

   trans : flag
       Transpose the table.

   Example:

   .. sourcecode:: rst

       .. table-data:: my/experiment/2011-02-*/data.json
          :data: x y result sub.result
          :link: %(path)s


Show data and images in table - :rst:dir:`table-data-and-image`
---------------------------------------------------------------

.. rst:directive:: .. table-data-and-image:: path [path ...]

   Search data under the given list of `path` and show matched data and
   corresponding image(s).

   base : string (newlines removed)
       The base path for searching data. Real path to be used
       will be `{BASE}/{ARG}` where `{ARG}` is each value in
       the arguments and `{BASE}` is the value of this option.

   data : text [, text, ...]
       A comma- or space-separated list of the "dictionary path".
       For each path, period-separated path such as 'a.b.c' or
       'alpha.0.1' can be used.

   image : text [, text, ...]
       A comma- or space-separated list of path to the images.
       The path is the relative path from the parent directory of
       the data file.

   widths : integer [, integer...]
       A comma- or space-separated list of relative column widths.
       Note that the first column is data sub-table and the second and
       the after are the images specified in `:image:`.

   image-{OPTION} : integer:{VAL} [, integer:{VAL} ...]
       `integer` is the index of the image.
       `{VAL}` specifies the value of the `{OPTION}` of the
       image directive.

   link : text [, text]
       A comma- or space-separated list of path to the link(s).
       Magic words ``%(path)s`` and ``%(relpath)s`` are available.

       ``%(path)s``
           This represents full path to the parent directory of the
           data file.
       ``%(relpath)s``
           This is the relative path of the ``%(path)s`` from the
           `base` directory.

   path-order : {'sort', 'sort_r'}
       Sort path or sort in the reversed order.

   sort : text [, text]
       A comma- or space-separated list of key.
       The table will be sorted by values of the keys.


   Example:

   .. sourcecode:: rst

       .. table-data-and-image:: my/experiment/2011-02-*/data.json
          :data: x y result sub.result
          :image: x_y_plot.png x_result_plot.png
          :link: %(path)s


See the difference of data - :rst:dir:`dictdiff`
------------------------------------------------

.. rst:directive:: .. dictdiff:: path [path ...]

   Search data under the given list of `path` and show the difference
   of the data.

   base : string (newlines removed)
       The base path for searching data. Real path to be used
       will be `{BASE}/{ARG}` where `{ARG}` is each value in
       the arguments and `{BASE}` is the value of this option.

   link : text [, text]
       A comma- or space-separated list of path to the link(s).
       Magic words ``%(path)s`` and ``%(relpath)s`` are available.

       ``%(path)s``
           This represents full path to the parent directory of the
           data file.
       ``%(relpath)s``
           This is the relative path of the ``%(path)s`` from the
           `base` directory.

   include : text [, text]
       A comma- or space-separated list of regular expression of the
       key to include.

   exclude : text [, text]
       A comma- or space-separated list of regular expression of the
       key to exclude.

   path-order : {'sort', 'sort_r'}
       Sort path or sort in the reversed order.

   trans : flag
       Transpose the table.

   Example:

   .. sourcecode:: rst

       .. dictdiff:: my/experiment/2011-02-*/data.json
          :link: %(path)s


Show effects of the parameter change - :rst:dir:`grid-images`
-------------------------------------------------------------

.. rst:directive:: .. grid-images:: path [path ...]

   Search data and show the images related to the data on "grid".
   The grid represents the *direct product* of the parameter set.
   This directive is useful to see the results of comprehensive
   experiments.  For example, to see the results from the experiment
   with the parameter *alpha* and *beta* which are chosen from
   *[0, 1]* and *[0.1, 0.5]*, use ``:param: alpha, beta``.
   The results will be shown in a 2x2 table.

   base : string (newlines removed)
       The base path for searching data. Real path to be used
       will be `{BASE}/{ARG}` where `{ARG}` is each value in
       the arguments and `{BASE}` is the value of this option.

   param : text [, text]
       A comma- or space-separated list of axis for making grid.

   image : text [, text]
       A comma- or space-separated list of path to the images.
       The path is the relative path from the parent directory of
       the data file.


Find images - :rst:dir:`find-images`
------------------------------------

.. rst:directive:: .. find-images:: path [path ...]

   Search images under the given list of `path` and show matched images.

   base : string (newlines removed)
       The base path for searching data. Real path to be used
       will be `{BASE}/{ARG}` where `{ARG}` is each value in
       the arguments and `{BASE}` is the value of this option.


List Pages - :rst:dir:`list-pages`
----------------------------------

.. rst:directive:: .. list-pages::

   Insert list of sub-pages.


Template page - ``_temp_``
==========================

The page which include ``_temp_`` in its URL is the template page.
The template page is used for generating page which is not exists
but the template page exists at the same level of the URL.

Example.:

    (a) ``/my/page/_temp_/``
    (b) ``/my/page/_temp_/_temp_/``
    (c) ``/my/page/_temp_/images/``
    (d) ``/my/page/_temp_/subdata/_temp_/``
    (e) ``/my/page/_temp_/_temp_/subdata``

    * ``/my/page/2011-05-21/`` matches to (a)
    * ``/my/page/2011-05-21/some-data/`` matches to (b)
    * ``/my/page/2011-05-21/images/`` matches to (c)
    * ``/my/page/2011-05-21/subdata/000/`` matches to (d)
    * ``/my/page/2011-05-21/000/subdata/`` matches to (e)
    * ``/my/page/2011-05-21/subdata/subdata/`` matches to (e)


``{{ args[N] }}`` (where ``N`` is an integer)
    N-th replacement of the ``_temp_`` in the URL.
    For example, at the page ``/my/page/2011-05-21/subdata/000/``
    in the above example, ``{{ args[0] }}`` and ``{{ args[1] }}``
    will be replaced by ``2011-05-21`` and ``000``.

``{{ path }}``
    This will be replaced by the full path to this directory.

``{{ relpath }}``
    This will be replaced by the relative path from the parent page of
    the leftmost ``_temp_`` page.
