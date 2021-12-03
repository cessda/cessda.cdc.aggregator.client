# Changelog

All notable changes to the CDC Aggregator Client will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security


## 0.2.0 - unreleased

### Added

- Sync entrypoint configuration option `--fail-on-parse` to
  make the processing fail out on errors during file parsing.

### Changed

- Default behaviour now is to skip files that cannot be parsed
  because of a MappingError. Other errors still lead to failures
  that terminate the processing. The behaviour can be controlled
  with `--fail-on-parse` configuration option.
  (Fixes [#11](https://bitbucket.org/cessda/cessda.cdc.aggregator.client/issues/11))

### Fixed

- Correct query for record with match in provenance information. This
  query is used to find duplicate records. Now a record is considered a
  duplicate if it has a matching item (baseUrl + identifier
  -combination) in list of provenances. New record always overwrites
  the old one.
  (Fixes [#12](https://bitbucket.org/cessda/cessda.cdc.aggregator.client/issues/12))


## 0.1.0 - 2021-09-21

### Added

- New codebase for CDC Aggregator Client.
- Support synchronizing records to CDC Aggregator DocStore.
