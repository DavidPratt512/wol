Changelog
=========

All changes to this project on and after 2021-09-24 will be logged here.

[Unreleased]
------------

- Refactoring of configuration code so it is actually readable and maintainable.
  This will likely come with a change in configuration logic as well.
- Refactoring of packet sending using dependency injection so testing is easier.
- Improved output to the console.
  See issue #9.

[0.1.0] - 2021-09-24
--------------------

Added
^^^^^

- This project now logs changes in this changelog.
- This project now follows a versioning scheme.
- This project now uses ``poetry`` for dependency management.
- This project now uses GitHub actions to execute unit tests on pushes to ``master`` and on all pull requests.
