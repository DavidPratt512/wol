Changelog
=========

All changes to this project on and after 2021-09-24 will be logged here.

[0.3.1] - 2023-04-01
--------------------

Added
^^^^^

- Add ``--version`` flag to CLI interface.

[0.3.0] - 2023-04-01
--------------------

Changed
^^^^^^^

- Respect ``XDG_CONFIG_HOME`` environment variable.
- Default location of ``wol.json`` config file has changed to
  ``${XDG_CONFIG_HOME:-~/.config}/wol/wol.json`` and
  ``%userprofile%\.config\wol\wol.json`` on unix-like and Windows machines,
  respectively.

[0.2.2] - 2022-02-15
--------------------

Changed
^^^^^^^

- Added long-form CLI arguments, such as ``--port`` and ``--repeat``.

[0.2.1] - 2021-10-01
--------------------

Changed
^^^^^^^

- The meaning and behavior of the ``repeat`` parameter has been clarified.
  If ``wake()`` is passed ``repeat=1``, the packet will be sent twice (repeated once).

[0.2.0] - 2021-09-25
--------------------

Changed
^^^^^^^

- Console output is now in a tabular format.
  See `issue #9 <https://github.com/DavidPratt512/wol/issues/9>`_.
- Cleaned up python imports in test files.
- Updated the license for 2021.

[0.1.0] - 2021-09-24
--------------------

Added
^^^^^

- This project now logs changes in this changelog.
- This project now follows a versioning scheme.
- This project now uses ``poetry`` for dependency management.
- This project now uses GitHub actions to execute unit tests on pushes to ``master`` and on all pull requests.
