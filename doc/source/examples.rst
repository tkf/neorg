.. contents::

Example usages of the special directives
========================================

.. _file-tree:

File tree
---------

The following examples assume we have the file tree under the
:envvar:`DATADIRPATH` like this::

    DATADIRPATH
    `- my/
       `- experiment/
          |- 2011-02-25-182001/
          |  |- graph_1.png
          |  |- graph_2.png
          |  `- data.json
          |
          |- 2011-02-25-182002/
          |  |- graph_1.png
          |  |- graph_2.png
          |  `- data.json
          |
          |- 2011-02-25-182003/
          |  |- graph_1.png
          |  |- graph_2.png
          |  `- data.json
          |
          |- 2011-02-26-182001/
          |  |- graph_1.png
          |  |- graph_2.png
          |  `- data.json
          |
          `- 2011-02-26-182002/
             |- graph_1.png
             |- graph_2.png
             `- data.json


.. _examples/table-data:

Example usages of :rst:dir:`table-data`
---------------------------------------

Basic example
^^^^^^^^^^^^^

.. sourcecode:: rst

    .. table-data:: my/experiment/2011-02-25-*/data.json
       :data: alpha beta result.gamma
       :link: %(path)s

will produce a table like this:

.. list-table:: Data found in: ``my/experiment/2011-02-25-*/data.json``
   :widths: 3 1 1 2 5
   :header-rows: 1

   * -
     - alpha
     - beta
     - result.gamma
     - link(s)
   * - my/experiment/2011-02-25-182001/data.json
     - 1
     - 0.1
     - 0.01
     - *(link to the page /my/experiment/2011-02-25-182001/)*
   * - my/experiment/2011-02-25-182002/data.json
     - 2
     - 0.2
     - 0.02
     - *(link to the page /my/experiment/2011-02-25-182001/)*
   * - my/experiment/2011-02-25-182003/data.json
     - 3
     - 0.3
     - 0.03
     - *(link to the page /my/experiment/2011-02-25-182003/)*


Use of ``:base:`` option
^^^^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: rst

    .. table-data:: 2011-02-25-*/data.json
                    2011-02-26-*/data.json
       :base: my/experiment
       :data: alpha beta result.gamma
       :link: %(relpath)s

will produce a table like this:

.. list-table:: Data found in:
                ``my/experiment/{2011-02-25-*/data.json, 2011-02-26-*/data.json}``
   :widths: 3 1 1 2 4
   :header-rows: 1

   * -
     - alpha
     - beta
     - result.gamma
     - link(s)
   * - 2011-02-25-182001/data.json
     - 1
     - 0.1
     - 0.01
     - *(link to the page 2011-02-25-182001/)*
   * - 2011-02-25-182002/data.json
     - 2
     - 0.2
     - 0.02
     - *(link to the page 2011-02-25-182001/)*
   * - 2011-02-25-182003/data.json
     - 3
     - 0.3
     - 0.03
     - *(link to the page 2011-02-25-182003/)*
   * - 2011-02-26-182001/data.json
     - 1
     - 0.2
     - 0.01
     - *(link to the page 2011-02-26-182001/)*
   * - 2011-02-26-182002/data.json
     - 2
     - 0.1
     - 0.02
     - *(link to the page 2011-02-26-182001/)*


Newest results on top
^^^^^^^^^^^^^^^^^^^^^

.. sourcecode:: rst

    .. table-data:: 2011-02-25-*/data.json
       :path-order: sort_r
       :base: my/experiment
       :data: alpha beta result.gamma
       :link: %(relpath)s

will produce a table like this:

.. list-table:: Data found in: ``my/experiment/2011-02-25-*/data.json``
   :widths: 3 1 1 2 4
   :header-rows: 1

   * -
     - alpha
     - beta
     - result.gamma
     - link(s)
   * - 2011-02-25-182003/data.json
     - 3
     - 0.3
     - 0.03
     - *(link to the page 2011-02-25-182003/)*
   * - 2011-02-25-182002/data.json
     - 2
     - 0.2
     - 0.02
     - *(link to the page 2011-02-25-182001/)*
   * - 2011-02-25-182001/data.json
     - 1
     - 0.1
     - 0.01
     - *(link to the page 2011-02-25-182001/)*


.. _examples/table-data-and-image:

Example usages of :rst:dir:`table-data-and-image`
-------------------------------------------------

Basic example
^^^^^^^^^^^^^

.. sourcecode:: rst

    .. table-data-and-image:: 2011-02-25-*/data.json
       :image: graph_1.png graph_2.png
       :path-order: sort_r
       :base: my/experiment
       :data: alpha beta result.gamma
       :link: %(relpath)s

will produce a table like this:

.. list-table:: Data found in: ``my/experiment/2011-02-25-*/data.json``
   :widths: 1 2 2

   * - .. list-table:: 2011-02-25-182003/data.json

          * - alpha
            - 3
          * - beta
            - 0.3
          * - result.gamma
            - 0.03

       - *(link to the page 2011-02-25-182003/)*

     - *(image of 2011-02-25-182003/graph_1.png)*
     - *(image of 2011-02-25-182003/graph_2.png)*

   * - .. list-table:: 2011-02-25-182002/data.json

          * - alpha
            - 2
          * - beta
            - 0.2
          * - result.gamma
            - 0.02

       - *(link to the page 2011-02-25-182002/)*

     - *(image of 2011-02-25-182002/graph_1.png)*
     - *(image of 2011-02-25-182002/graph_2.png)*

   * - .. list-table:: 2011-02-25-182001/data.json

          * - alpha
            - 1
          * - beta
            - 0.1
          * - result.gamma
            - 0.01

       - *(link to the page 2011-02-25-182001/)*

     - *(image of 2011-02-25-182001/graph_1.png)*
     - *(image of 2011-02-25-182001/graph_2.png)*


Scaling image
^^^^^^^^^^^^^

To scale the image with the table, you can use ``:image-width:``
option.

.. sourcecode:: rst

    .. table-data-and-image:: 2011-02-25-*/data.json
       :image: graph_1.png
       :image-width: 0:100%
       :path-order: sort_r
       :base: my/experiment
       :data: alpha beta result.gamma
       :link: %(relpath)s

will produce a table like this:

.. list-table:: Data found in: ``my/experiment/2011-02-25-*/data.json``
   :widths: 1 2

   * - .. list-table:: 2011-02-25-182003/data.json

          * - alpha
            - 3
          * - beta
            - 0.3
          * - result.gamma
            - 0.03

       - *(link to the page 2011-02-25-182003/)*

     - *(image of 2011-02-25-182003/graph_1.png)*

       <- the width varied with the width of the table. ->

   * - .. list-table:: 2011-02-25-182002/data.json

          * - alpha
            - 2
          * - beta
            - 0.2
          * - result.gamma
            - 0.02

       - *(link to the page 2011-02-25-182002/)*

     - *(image of 2011-02-25-182002/graph_1.png)*

   * - .. list-table:: 2011-02-25-182001/data.json

          * - alpha
            - 1
          * - beta
            - 0.1
          * - result.gamma
            - 0.01

       - *(link to the page 2011-02-25-182001/)*

     - *(image of 2011-02-25-182001/graph_1.png)*


.. _examples/dictdiff:

Example usages of :rst:dir:`dictdiff`
-------------------------------------

Basic example
^^^^^^^^^^^^^

.. sourcecode:: rst

    .. dictdiff:: 2011-02-25-*/data.json
       :base: my/experiment
       :link: %(relpath)s


.. list-table:: Diff of data found in:
                ``my/experiment/2011-02-25-*/data.json``
   :widths: 3 1 1 1 2 5
   :header-rows: 1

   * -
     - seed
     - alpha
     - beta
     - result.gamma
     - link(s)
   * - my/experiment/2011-02-25-182001/data.json
     - 8906300472
     - 1
     - 0.1
     - 0.01
     - *(link to the page /my/experiment/2011-02-25-182001/)*
   * - my/experiment/2011-02-25-182002/data.json
     - 2634932505
     - 2
     - 0.2
     - 0.02
     - *(link to the page /my/experiment/2011-02-25-182001/)*
   * - my/experiment/2011-02-25-182003/data.json
     - 2510325972
     - 3
     - 0.3
     - 0.03
     - *(link to the page /my/experiment/2011-02-25-182003/)*


Exclude data
^^^^^^^^^^^^

If you don't want to see ``seed`` in the data, you can exclude it
using the ``:exclude:`` option.

.. sourcecode:: rst

    .. dictdiff:: 2011-02-25-*/data.json
       :base: my/experiment
       :link: %(relpath)s
       :exclude: seed


.. list-table:: Diff of data found in:
                ``my/experiment/2011-02-25-*/data.json``
   :widths: 3 1 1 2 5
   :header-rows: 1

   * -
     - alpha
     - beta
     - result.gamma
     - link(s)
   * - my/experiment/2011-02-25-182001/data.json
     - 1
     - 0.1
     - 0.01
     - *(link to the page /my/experiment/2011-02-25-182001/)*
   * - my/experiment/2011-02-25-182002/data.json
     - 2
     - 0.2
     - 0.02
     - *(link to the page /my/experiment/2011-02-25-182001/)*
   * - my/experiment/2011-02-25-182003/data.json
     - 3
     - 0.3
     - 0.03
     - *(link to the page /my/experiment/2011-02-25-182003/)*


.. _examples/grid-images:

Example usages of :rst:dir:`grid-images`
----------------------------------------

Basic example
^^^^^^^^^^^^^

.. sourcecode:: rst

    .. grid-images:: 2011-02-25-*[12]/data.json
                     2011-02-26-*/data.json
       :base: my/experiment
       :image: graph_1.png
       :param: alpha beta

.. list-table:: Comparing images of data found in:
                ``my/experiment{2011-02-25-*[12]/data.json, 2011-02-26-*/data.json}``
   :widths: 1 5 5

   * -
     - **beta=0.1**
     - **beta=0.2**
   * - **alpha=1**
     - *(image of 2011-02-25-182001/graph_1.png)*
     - *(image of 2011-02-26-182001/graph_1.png)*
   * - **alpha=2**
     - *(image of 2011-02-26-182002/graph_1.png)*
     - *(image of 2011-02-25-182002/graph_1.png)*


.. _examples/find-images:

Example usage of :rst:dir:`find-images`
---------------------------------------

.. sourcecode:: rst

    .. find-images:: 2011-02-25-*/graph_1.png
       :base: my/experiment

will produce paragraphs like this:

    my/experiment/2011-02-25-182001/graph_1.png

    *(image of 2011-02-25-182001/graph_1.png)*

    my/experiment/2011-02-25-182002/graph_1.png

    *(image of 2011-02-25-182002/graph_1.png)*

    my/experiment/2011-02-25-182003/graph_1.png

    *(image of 2011-02-25-182003/graph_1.png)*


.. _examples/template-page:

Example usages of the template page
===================================

With the above data tree, you may want to generate the similar page
when you access the page ``/my/experiment/...``.  For that purpose,
you can make a :term:`template page` ``/my/experiment/_temp_`` with
the following contents:

.. sourcecode:: rst

   Table data
   ==========

   .. table-data:: data.json
      :base: my/experiment/{{ args[0] }}/
      :data: *
      :trans:
      :widths: 1 9

   Images
   ======

    .. find-images:: *.png
       :base: my/experiment/{{ args[0] }}/

This :term:`template page` generates the following page when you
access to the page ``/my/experiment/2011-02-25-182001``.

.. sourcecode:: rst

   Table data
   ==========

   .. table-data:: data.json
      :base: my/experiment/2011-02-25-182001/
      :data: *
      :trans:
      :widths: 1 9

   Images
   ======

    .. find-images:: *.png
       :base: my/experiment/2011-02-25-182001/

Note that ``{{ args[0] }}`` is replaced by ``2011-02-25-182001``.


The above page can also be generated by the following template pages:

.. sourcecode:: rst

   .. an example using "relpath"

   Table data
   ==========

   .. table-data:: data.json
      :base: my/experiment/{{ relpath }}
      :data: *
      :trans:
      :widths: 1 9

   Images
   ======

    .. find-images:: *.png
       :base: my/experiment/{{ relpath }}

and

.. sourcecode:: rst

   .. an example using "path"

   Table data
   ==========

   .. table-data:: data.json
      :base: {{ path }}
      :data: *
      :trans:
      :widths: 1 9

   Images
   ======

    .. find-images:: *.png
       :base: {{ path }}
