# Changelog

All notable changes to the CDC Aggregator Client will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## 0.3.0 - 2022-05-18

### Changed

- Generate `Study._aggregator_identifier` using OAI-PMH provenance info.
  (Implements [#20](https://bitbucket.org/cessda/cessda.cdc.aggregator.client/issues/20))
- Require CDCAGG Common 0.3.0


## 0.2.1 - 2022-04-05

### Changed

- Use 1.0.0 releases of Kuha Common and Kuha Client dependencies in
  requirements.txt.

### Fixed

- Updating an existing record must not change the
  `_aggregator_identifier` value.
  (Fixes [#19](https://bitbucket.org/cessda/cessda.cdc.aggregator.client/issues/19))


## 0.2.0 - 2021-12-17
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5779783.svg)](https://doi.org/10.5281/zenodo.5779783)

### Added

- Sync entrypoint configuration option `--fail-on-parse` to
  make the processing fail out on errors during file parsing.

### Changed

- Default behaviour now is to skip files that cannot be parsed
  because of a MappingError. Other errors still lead to failures
  that terminate the processing. The behaviour can be controlled
  with `--fail-on-parse` configuration option.
  (Fixes [#11](https://bitbucket.org/cessda/cessda.cdc.aggregator.client/issues/11))
- Update dependencies in requirements.txt

  - ConfigArgParse 1.5.3
  - Kuha Common to Git commit 8e7de1f16530decc356fee660255b60fcacaea23
  - Kuha Client to Git commit 46ba0501e92f6db3475d721344f456627c01f459
  - Aggregator Shared Library 0.2.0

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
