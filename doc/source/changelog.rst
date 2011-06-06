ChangeLog
=========

v0.0.2
^^^^^^

- Check system version before running ``neorg serve`` command.
- If neorg page creation clashes, show the python traceback so that
  user still can edit the page to workaround the problem.
- Bug fixes:

  - ``(/link/)`` did not converted to a link
  - :rst:dir:`table-data` and :rst:dir:`table-data-and-image`
    clashed if the `widths` parameter is too short.
  - etc.


v0.0.1
^^^^^^

- The first release.
