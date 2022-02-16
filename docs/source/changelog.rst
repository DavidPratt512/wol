Changelog
=========

All changes to this project on and after 2021-09-24 will be logged here.

[Unreleased]
------------

- Refactoring of configuration code so it is actually readable and maintainable.
  This will likely come with a change in configuration logic as well.
- Refactoring of packet sending using dependency injection so testing is easier.

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
