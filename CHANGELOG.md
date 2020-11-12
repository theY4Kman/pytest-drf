# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased]


## [1.1.2] — 2020-11-12
### Fixed
 - Resolve `typing.Protocol` `ImportError` on Python version 3.6 and 3.7


## [1.1.1] — 2020-11-02
### Fixed
 - Resolve error when running `py.test --fixtures`


## [1.1.0] - 2020-08-26
### Added
 - Exposed `url_for`, a compact wrapper around Django's `reverse()` to generate URLs succinctly
 - Add docs/tutorial to README


## [1.0.4] - 2020-08-22
### Fixed
 - Prefix all test methods with `test_`, so they work with standard pytest configuration (previously, tests were prefixed with `it_`, which required `python_functions` to include `it_*` in `pytest.ini`)


## [1.0.3] - 2020-08-21
### Changed
 - Switched to [pytest-djangoapp](https://github.com/idlesign/pytest-djangoapp) (from [pytest-django](https://github.com/pytest-dev/pytest-django)) for testing


## [1.0.2] - 2020-08-04
### Changed
 - Relaxed version pin on `pytest-assert-utils`


## [1.0.1] - 2020-08-03
### Changed
 - Included LICENSE, CHANGELOG, and tests in source distribution


## [1.0.0] - 2020-08-03
### Added
 - Introducing `pluralized` to ease use of expression methods
 - Added tests

### Changed
 - `ForbidsAnonymousUsers` now expects a 403 status code, matching DRF's default permissions behaviour

### Fixed
 - Resolved incorrect MRO when declaring `UsesXYZMethod` base classes after `APIViewTest`
 - Properly handle `headers` kwarg in API test client
 - Prevent unintended Django settings accesses before pytest-django can set `DJANGO_SETTINGS_MODULE`


## [0.1.0] - 2019-04-22
### Added
 - Introducing `APIViewTest` and `ViewSetTest` for quick scaffolding of DRF API tests
