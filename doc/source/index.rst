.. contents::

=========================
  NEOrg Reference Guide
=========================


.. _special-directives:

Special directives
==================

A :term:`directive` is a general reST block markup.
With the special directives defined by NEOrg, you can fetch data and
images, show them effectively, and organize your notes.


Show data in a table - :rst:dir:`table-data`
--------------------------------------------

.. rst:directive:: .. table-data:: path [path ...]

   Search data file under the given list of `path` and show matched
   data.
   You can use :term:`Unix shell-style pattern matching`.

   base : string (newlines removed)
       This is an optional parameter to specify the directory
       where the data files are searched from.
       The data files will be searched from :envvar:`DATADIRPATH` if
       not specified.

       For example,

       .. sourcecode:: rst

           .. table-data:: 2011-02-*/data.json
                           2011-03-*/data.json
              :base: my/experiment

       will search the files matches to
       ``my/experiment/2011-02-*/data.json`` and
       ``my/experiment/2011-03-*/data.json``.

   data : text [, text, ...]
       A comma- or space-separated list of the :term:`dictionary path`.
       You can use :term:`Unix shell-style pattern matching`.

   widths : integer [, integer...]
       A comma- or space-separated list of relative column widths.

   link : text [, text]
       A comma- or space-separated list of path to the link(s).
       Magic words ``%(path)s`` and ``%(relpath)s`` are available.

       ``%(path)s``
           This represents full path to the parent directory of the
           data file.
       ``%(relpath)s``
           This is the relative path of the ``%(path)s`` from the
           :term:`base` directory.

   path-order : {'sort', 'sort_r'}
       Sort the matched data paths.
       ``sort`` will sort the paths in alphabetical order
       and ``sort_r`` is the reversed version of ``sort``.
       The default is ``'sort'``.
       Note that

       .. sourcecode:: rst

           .. table-data:: 2011-02-*/data.json
                           2011-03-*/data.json
              :path-order: sort_r

       does not makes ``2011-03-01/data.json`` higher than
       ``2011-02-01/data.json``.  You will need to write

       .. sourcecode:: rst

           .. table-data:: 2011-03-*/data.json
                           2011-02-*/data.json
              :path-order: sort_r

   trans : flag
       Transpose the table.

   .. seealso:: :ref:`examples/table-data`


Show data and images in a table - :rst:dir:`table-data-and-image`
-----------------------------------------------------------------

.. rst:directive:: .. table-data-and-image:: path [path ...]

   Search data under the given list of `path` and show matched data and
   corresponding image(s).
   You can use :term:`Unix shell-style pattern matching`.

   base : string (newlines removed)
       This is an optional parameter to specify the directory
       where the data files are searched from.
       See :rst:dir:`table-data` for the details.

   data : text [, text, ...]
       A comma- or space-separated list of the :term:`dictionary path`.
       See :rst:dir:`table-data` for the details.

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
       `image directive`_.

   link : text [, text]
       A comma- or space-separated list of path to the link(s).
       See :rst:dir:`table-data` for the details.

   path-order : {'sort', 'sort_r'}
       Sort the matched data paths.
       See :rst:dir:`table-data` for the details.

   sort : text [, text]
       A comma- or space-separated list of the :term:`dictionary path`.
       The table will be sorted by values of the keys.

   .. seealso:: :ref:`examples/table-data-and-image`

.. _`image directive`:
   http://docutils.sourceforge.net/docs/ref/rst/directives.html#image


See the difference of data - :rst:dir:`dictdiff`
------------------------------------------------

.. rst:directive:: .. dictdiff:: path [path ...]

   Search data under the given list of `path` and show the difference
   of the data.
   You can use :term:`Unix shell-style pattern matching`.

   base : string (newlines removed)
       This is an optional parameter to specify the directory
       where the data files are searched from.
       See :rst:dir:`table-data` for the details.

   link : text [, text]
       A comma- or space-separated list of path to the link(s).
       See :rst:dir:`table-data` for the details.

   include : text [, text]
       A comma- or space-separated list of :term:`regular expression`
       of the :term:`dictionary path` to include.

   exclude : text [, text]
       A comma- or space-separated list of :term:`regular expression`
       of the :term:`dictionary path` to exclude.

   path-order : {'sort', 'sort_r'}
       Sort the matched data paths.
       See :rst:dir:`table-data` for the details.

   trans : flag
       Transpose the table.

   .. seealso:: :ref:`examples/dictdiff`


Show effects of the parameter change - :rst:dir:`grid-images`
-------------------------------------------------------------

.. rst:directive:: .. grid-images:: path [path ...]

   Search data and show the images related to the data on "**grid**".
   You can use :term:`Unix shell-style pattern matching`.

   In experiments, you may change parameters systematically
   to see what will happen.  For example, when you do experiments
   varying two parameters *a=1, 2, 3* and *b=0.1, 0.2, 0.3*,
   you will get 9 results.  Viewing the results in a linear list is
   a bad idea: you should see it in a 3x3 matrix like this!:

   .. list-table::
      :widths: 1 5 5 5

      * -
        - **b=0.1**
        - **b=0.2**
        - **b=0.3**
      * - **a=1**
        - result with *a=1* and *b=0.1*
        - result with *a=1* and *b=0.2*
        - result with *a=1* and *b=0.3*
      * - **a=2**
        - result with *a=2* and *b=0.1*
        - result with *a=2* and *b=0.2*
        - result with *a=2* and *b=0.3*
      * - **a=3**
        - result with *a=3* and *b=0.1*
        - result with *a=3* and *b=0.2*
        - result with *a=3* and *b=0.3*

   The grid is a N-dimensional version of this matrix.
   To see it in 2D display (because we don't have N-dim display),
   NEOrg generates the nested table.

   base : string (newlines removed)
       The base path for searching data. Real path to be used
       This is an optional parameter to specify the directory
       where the data files are searched from.
       See :rst:dir:`table-data` for the details.

   param : text [, text]
       A comma- or space-separated list of the :term:`dictionary path`
       for the axes of the grid.

   image : text [, text]
       A comma- or space-separated list of path to the images.
       The path is the relative path from the parent directory of
       the data file.

   .. seealso:: :ref:`examples/grid-images`


Find images - :rst:dir:`find-images`
------------------------------------

.. rst:directive:: .. find-images:: path [path ...]

   Search images under the given list of `path` and show matched images.
   You can use :term:`Unix shell-style pattern matching`.

   base : string (newlines removed)
       This is an optional parameter to specify the directory
       where the data files are searched from.
       See :rst:dir:`table-data` for the details.

   .. seealso:: :ref:`examples/find-images`


List Pages - :rst:dir:`list-pages`
----------------------------------

.. rst:directive:: .. list-pages::

   Insert list of sub-pages.


.. _template-page:

Template page - ``_temp_``
==========================

When you do experiments repeatedly, you may want to see the results
in a fixed format.  The template page can be used for that purpose.

The page which has ``_temp_`` in its :term:`page path` is a
:term:`template page`.
The template page is used for generating page.
If the page path does not exist but the template page which matches to
the page path exists, generated page will be shown.

Examples of the template :term:`page path`:

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

.. seealso:: :ref:`examples/template-page`


Glossary
========

.. glossary::

   directive
       A directive is one of the reST block markup in the following
       shape:

       .. sourcecode:: rst

          .. directive-name:: argument(s)
             :option: parameter
             :another_option: another_parameter

             some contents

       See `reStructuredText Directives`_ for more information and
       the basic directives defined by docutils.

       NEOrg defines varikous special for displaying and organizing
       data effectively (see :ref:`special-directives`).

   page path
       The page path is the URL to the page.

   unix shell-style pattern matching
       Unix shell-style pattern matching supports the following
       wild-cards.

       +------------+------------------------------------+
       | Pattern    | Meaning                            |
       +============+====================================+
       | ``*``      | matches everything                 |
       +------------+------------------------------------+
       | ``?``      | matches any single character       |
       +------------+------------------------------------+
       | ``[seq]``  | matches any character in *seq*     |
       +------------+------------------------------------+
       | ``[!seq]`` | matches any character not in *seq* |
       +------------+------------------------------------+

   ``base``
       This is the optional parameter for the directives which searches
       the data files.
       See :rst:dir:`table-data` for the details.

   ``link``
       This is the optional parameter for the directives which generates
       the links to the other pages.
       See :rst:dir:`table-data` for the details.

   magic words
       Magic words are the special words which are replaced by NEOrg.

       Magic words ``%(path)s`` and ``%(relpath)s`` are available
       in the :term:`link` parameter.

       Magic words ``%(root)s`` and ``%(neorg)s`` are available in the
       configuration file for the variables :envvar:`DATADIRPATH` and
       :envvar:`DATABASE`.

   dictionary path
       To specify the value in the nested dictionary, NEOrg uses
       period-separated keys.  For example, the values in the
       following nested dictionary can be accessed by the
       "dictionary path" such as ``'key1.nestedkey1'``.

       .. sourcecode:: js

          {'key1': {
               'nestedkey1': 1,
               'nestedkey2': 2
           }
           'key2': 2
          }

   regular expression
       NEOrg uses python regular expression to filtering out/in
       :term:`dictionary path`.

       See `Regular Expression Syntax --- Python documentation`_ for
       more information about the regular expression syntax.

   template page
       A template page is the page which has at least one ``_temp_``
       in its :term:`page path`.
       See also :ref:`template-page`.

   debug mode
       In debug mode, python interactive shell will be invoked in your
       browser when NEOrg clashes.
       See `Debugging Applications -- Werkzeug documentation`_ and
       `Debug Mode --- Flask documentation`_  for more information.

       .. warning::

          If someone can access to
          NEOrg running in debug mode, he can do anything your python
          can do, such as deleting files.  Thus, **debug mode should
          not be used on an untrusted network.**

.. _`Regular Expression Syntax --- Python documentation`:
   http://docs.python.org/library/re.html#re-syntax
.. _`Debugging Applications -- Werkzeug documentation`:
   http://werkzeug.pocoo.org/docs/debug/
.. _`Debug Mode --- Flask documentation`:
   http://flask.pocoo.org/docs/quickstart/#debug-mode


Configuration variables
=======================

.. envvar:: DATADIRPATH

   Path to your data directory.
   :term:`Magic words` ``%(root)s`` and ``%(neorg)s`` are available.
   The string ``~`` will be replaced by the user's home directory.
   Also, the environment variables are available.  For example, you
   can also use ``$HOME`` or ``${HOME}`` to specify your home directory.
   The default is ``%(root)s``.

   ``%(root)s``
       The directory you specified by ``neorg init`` command.
       If you did not specify, this is the directory where you ran
       ``neorg init`` command.

   ``%(neorg)s``
       This is equivalent to ``%(root)s/.neorg/``.

.. envvar:: DATABASE

   The path to the sqlite data base file.
   :term:`Magic words` ``%(root)s`` and ``%(neorg)s``,
   special character ``~``, and the environment variables are available.
   The default is ``'%(neorg)s/neorg.db'``.

.. envvar:: DEBUG

   If it is set to ``True``, ``neorg serve`` runs in :term:`debug mode`
   always.


FAQs
====

How do I make a new page?
-------------------------

Just type a page path to the browser's address bar, e.g.::

    http://localhost:8000/my/new/page/

and then you will see the edit form, if the page does not exist.


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


Other contents
==============

.. toctree::
   :maxdepth: 1

   examples
   commands
