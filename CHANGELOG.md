# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased


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
