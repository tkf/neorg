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
       A comma- or comma-separated list of the "dictionary path".
       For each path, period-separated path such as 'a.b.c' or
       'alpha.0.1' can be used.

   widths : integer [, integer...]
       A comma- or space-separated list of relative column widths.
       Note that the first column is data sub-table and the second and
       the after are the images specified in `:image:`.

   link : text [, text]
       A comma- or comma-separated list of path to the link(s).
       Magic words ``%(path)s`` and ``%(relpath)s`` are available.

       ``%(path)s``
           This represents full path to the parent directory of the
           data file.
       ``%(relpath)s``
           This is the relative path of the ``%(path)s`` from the
           `base` directory.

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
       A comma- or comma-separated list of the "dictionary path".
       For each path, period-separated path such as 'a.b.c' or
       'alpha.0.1' can be used.

   image : text [, text, ...]
       A comma- or comma-separated list of path to the images.
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
       A comma- or comma-separated list of path to the link(s).
       Magic words ``%(path)s`` and ``%(relpath)s`` are available.

       ``%(path)s``
           This represents full path to the parent directory of the
           data file.
       ``%(relpath)s``
           This is the relative path of the ``%(path)s`` from the
           `base` directory.


   Example:

   .. sourcecode:: rst

       .. table-data-and-image:: my/experiment/2011-02-*/data.json
          :data: x y result sub.result
          :image: x_y_plot.png x_result_plot.png
          :link: %(path)s


Find images - :rst:dir:`find-images`
------------------------------------

.. rst:directive:: .. find-images:: path [path ...]

   Search images under the given list of `path` and show matched images.

   base : string (newlines removed)
       The base path for searching data. Real path to be used
       will be `{BASE}/{ARG}` where `{ARG}` is each value in
       the arguments and `{BASE}` is the value of this option.


Template page - ``<temp>``
==========================

The page which include ``<temp>`` in its URL is the template page.
The template page is used for generating page which is not exists
but the template page exists at the same level of the URL.

Example.:

    (a) ``/my/page/<temp>/``
    (b) ``/my/page/<temp>/<temp>/``
    (c) ``/my/page/<temp>/images/``
    (d) ``/my/page/<temp>/subdata/<temp>/``
    (e) ``/my/page/<temp>/<temp>/subdata``

    * ``/my/page/2011-05-21/`` matches to (a)
    * ``/my/page/2011-05-21/some-data/`` matches to (b)
    * ``/my/page/2011-05-21/images/`` matches to (c)
    * ``/my/page/2011-05-21/subdata/000/`` matches to (d)
    * ``/my/page/2011-05-21/000/subdata/`` matches to (e)
    * ``/my/page/2011-05-21/subdata/subdata/`` matches to (e)


``{{ args[N] }}`` (where ``N`` is an integer)
    N-th replacement of the ``<temp>`` in the URL.
    For example, at the page ``/my/page/2011-05-21/subdata/000/``
    in the above example, ``{{ args[0] }}`` and ``{{ args[1] }}``
    will be replaced by ``2011-05-21`` and ``000``.

``{{ path }}``
    This will be replaced by the full path to this directory.

``{{ relpath }}``
    This will be replaced by the relative path from the parent page of
    the leftmost ``<temp>`` page.
