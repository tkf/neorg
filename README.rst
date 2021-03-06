NEOrg - Numerical Experiment Organizer
======================================

NEOrg is a wiki to organize your experimental data.
NEOrg provides two features:

1. Special directives.

   A `directive` is a general reST block markup.
   With the special directives defined by NEOrg, you can fetch data and
   images, show them effectively, and organize your notes.

2. Template page.

   When you do experiments repeatedly, you may want to see the results
   in a fixed format.  The template page can be used for that purpose.

See the document_ for more!


Install
-------

::

    pip install neorg  # or
    easy_isntall neorg


If you want to try the newest (possibly unstable) version, you can
install it from https://github.com/tkf/neorg.::

    pip install -e git://github.com/tkf/neorg.git#egg=neorg


Quick start
-----------

::

    cd directory/where/you/store/experimental/data
    neorg init
    neorg serve --browser


Dependencies
------------

- `docutils`, `Flask`, `Whoosh` and `argparse`
- `PyYAML` to load YAML data (optional).

For development:

- `nose` and `mock` for unit tests
- `texttable` for doctest
- `sphinx` for building document

Javascript libraries (included):

- `jQuery <http://jquery.com/>`_
- `ColorBox <http://colorpowered.com/colorbox/>`_
- `jquery.hotkeys <https://github.com/tzuryby/jquery.hotkeys>`_


Links
-----

- `project page`_
- document_
- `issue tracking`_
- `change log`_
- You can see screenshots in
  `my blog post <http://tkf.github.com/2011/06/04/neorg-0.0.1.html>`_.

.. _`project page`: https://github.com/tkf/neorg
.. _document: https://neorg.readthedocs.org/
.. _`issue tracking`: https://github.com/tkf/neorg/issues
.. _`change log`: http://neorg.readthedocs.org/en/latest/changelog.html
