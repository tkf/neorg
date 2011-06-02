NEOrg commands
==============

.. admonition:: NEOrg sub-commands

   * init_
   * serve_

.. [[[cog from genecommands import genehelp; genehelp() ]]]

::

    usage: neorg [-h] {init,serve} ...

    NEOrg - Numerical Simulation Organizer

    positional arguments:
      {init,serve}
        init        initialize neorg directory
        serve       start stand-alone webserver

    optional arguments:
      -h, --help    show this help message and exit

.. [[[end]]]


``init``
--------

.. [[[cog from genecommands import genehelp; genehelp('init') ]]]

::

    usage: neorg init [-h] [dest]

    positional arguments:
      dest        root directory to initialize (default: ".")

    optional arguments:
      -h, --help  show this help message and exit

.. [[[end]]]


``serve``
---------

.. [[[cog from genecommands import genehelp; genehelp('serve') ]]]

::

    usage: neorg serve [-h] [-p PORT] [-R ROOT] [-b] [--debug]

    optional arguments:
      -h, --help            show this help message and exit
      -p PORT, --port PORT  port to listen (default: 8000)
      -R ROOT, --root ROOT  root directory (where `.neorg/` exists)
      -b, --browser         open web browser
      --debug               set DEBUG=True to run in debug mode

.. [[[end]]]
