Special directives
==================


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


Template page (``<temp>``)
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

    * ``/my/page/2011-05-21/_der`` matches to (a)
    * ``/my/page/2011-05-21/some-data/_der`` matches to (b)
    * ``/my/page/2011-05-21/images/_der`` matches to (c)
    * ``/my/page/2011-05-21/subdata/000/_der`` matches to (d)
    * ``/my/page/2011-05-21/000/subdata/_der`` matches to (e)
    * ``/my/page/2011-05-21/subdata/subdata/_der`` matches to (e)


``{{ args[N] }}`` (where ``N`` is an integer)
    N-th replacement of the ``<temp>`` in the URL.
    For example, at the page ``/my/page/2011-05-21/subdata/000/_der``
    in the above example, ``{{ args[0] }}`` and ``{{ args[1] }}``
    will be replaced by ``2011-05-21`` and ``000``.

``{{ path }}``
    This will be replaced by the full path to this directory.

``{{ relpath }}``
    This will be replaced by the relative path from the parent page of
    the leftmost ``<temp>`` page.
