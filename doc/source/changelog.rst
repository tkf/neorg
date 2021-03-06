ChangeLog
=========

v0.0.4
^^^^^^

- Added image preview window.
  Clicking image opens a modal window to show the image without page
  transition.

  - In preview window, navigation using left/right/up/down keys is
    supported.
  - This navigation does not work for 3D or more dimensional
    :rst:dir:`grid-images`.

- Added `link` option to :rst:dir:`grid-images`.
- Added `file` option to :rst:dir:`table-data`,
  :rst:dir:`table-data-and-image`, :rst:dir:`dictdiff`,
  :rst:dir:`find-images`, and :rst:dir:`grid-images`.
- Added `ftype-{pickle,python,yaml,json}` options to
  :rst:dir:`table-data`, :rst:dir:`table-data-and-image` and
  :rst:dir:`dictdiff` so that they can read the data files
  with unsupported extensions.
- Added :rst:dir:`recent-pages`.

v0.0.3
^^^^^^

- Pages can be searched from the right top search box.
- :rst:dir:`table-data-and-image` highlights data with different
  values.
- :rst:dir:`list-pages` shows sub-pages as a nested list, not as a
  flat list.
- Show sub-pages when the accessed page does not exist but at least
  one sub-page exists.
- Use reversed :term:`page path` as a page title.

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
