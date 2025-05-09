# Changelog

All notable changes to the CDC Aggregator Client will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## 0.11.0 - 2025-05-09

### Added

- Support reading DDI 3.2 XML metadata from OAI-PMH
  envelope. (Implements
  [#41](https://github.com/cessda/cessda.cdc.aggregator.client/issues/41))

### Changed

- DDI 3.3 mapping now removes whitespaces and surrounding line breaks from values that get read into following attributes:
  - Study.data_access
  - Study.data_access_descriptions
  - Study.citation_requirements
  - Study.deposit_requirements
- DDI 3.3 mapping now uses XPATH
  `/ddi:DDIInstance/s:StudyUnit/r:UserID` with
  `@typeOfUserID="StudyNumber"`as a primary source for
  Study.identifiers. If this is found, all other XPATH sources are
  skipped. If this is not found, the old behaviour applies. (Implements
  [#42](https://github.com/cessda/cessda.cdc.aggregator.client/issues/42))
- DDI 3.3 mapping now uses XPATH
  `/ddi:DDIInstance/s:StudyUnit/a:Archive/a:ArchiveSpecific/a:Item/a:Access/r:Description/r:Content`
  as a primary source to map to Study.data_access. If the primary is
  found, all other XPATH sources are skipped. If the primary is not found,
  the old behaviour applies. (Implements
  [#43](https://github.com/cessda/cessda.cdc.aggregator.client/issues/43))
- DDI 3.3 mapping now uses
  `/ddi:DDIInstance/s:StudyUnit/a:Archive/a:ArchiveSpecific/a:Item/a:Access/a:TypeOfAccess`
  and its `@controlledVocabularyName` for primary XPATH source for
  Study.data_access_descriptions. If this is found, all other XPATH
  sources are skipped. If this is not found, the old behaviour
  applies. (Implements
  [#44](https://github.com/cessda/cessda.cdc.aggregator.client/issues/44))
- Require Aggregator Shared Library 0.10.0 in requirements.txt & setup.py.
- Require Kuha Common 2.7.0 in requirements.txt & setup.py.


## 0.10.0 - 2025-01-17

**Note:** After upgrade the file-cache should be removed to make sure
all files are re-read and saved to Document Store.

### Added

- Support more DDI-C elements. (Implements
  [#39](https://github.com/cessda/cessda.cdc.aggregator.client/issues/39))

  - Map DDI-C `/codeBook/stdyDscr/citation/distStmt/distDate` to
    `Study.distribution_dates`.
  - Map DDI-C `/codeBook/stdyDscr/method/dataColl/resInstru` to
    `Study.research_instruments`.
  - Map DDI-C `/codeBook/stdyDscr/dataAccs/useStmt/conditions/@elementVersion`
    to `Study.data_access_descriptions.attr_element_version`.
  - Map DDI-C `/codeBook/stdyDscr/stdyInfo/sumDscr/collDate` CDATA
    to `Study.collection_periods.attr_description`.

### Changed

- Require Aggregator Shared Library 0.9.0 in requirements.txt.
- Require Kuha Common 2.6.0 in requirements.txt.
- Require Kuha Client 1.6.0 in requirements.txt.
- Require Tornado 6.4.2 in requirements.txt.


## 0.9.0 - 2024-08-30

### Added

- Support Python 3.11 & 3.12.
- New test environment for tox 'warnings-as-errors' to treat warnings
  as errors in tests. Run this environment in CI with latest python.

### Changed

- Require Aggregator Shared Library 0.8.1 in requirements.txt.
- Require Kuha Common 2.5.0 in requirements.txt.
- Require Kuha Client 1.5.0 in requirements.txt.
- Require Py12fLogging 0.7.0 in requirements.txt.
- Require Tornado 6.4.1 in requirements.txt.
- Require ConfigArgParse 1.7 in requirements.txt.

### Fixed

- Fix random `ResourceWarning: unclosed event loop` when running
  tests. KuhaUnitTestCase does not properly close the event
  loop on tearDown. Migrate away from KuhaUnitTestCase and use
  unittest.IsolatedAsyncioTestCase when running coroutines is
  required.


## 0.8.0 - 2024-04-30

### Added

- Map DDI-C `/codeBook/stdyDscr/citation/rspStmt/AuthEnty/ExtLink` to
  Study.principal_investigator attributes `external_link`,
  `external_link_uri`, `external_link_role` and `external_link_title`.

### Changed

- Update dependencies:

  - Require Aggregator Shared Library 0.7.0 in requirements.txt and
    setup.py. (Implements
    [#35](https://github.com/cessda/cessda.cdc.aggregator.client/issues/35))
  - Require Kuha Common 2.4.0 in requirements.txt and setup.py. Change
    URL to point to new source at gitlab.tuni. (Implements
    [#35](https://github.com/cessda/cessda.cdc.aggregator.client/issues/35))
  - Require Kuha Client 1.4.0 in requirements.txt and setup.py. Change
    URL to point to new source at gitlab.tuni. (Implements
    [#35](https://github.com/cessda/cessda.cdc.aggregator.client/issues/35))


## 0.7.0 - 2023-11-24

### Added

- Support `Study._direct_base_url`. (Implements
  [#33](https://github.com/cessda/cessda.cdc.aggregator.client/issues/33))


### Changed

- Update dependencies: Require Aggregator Shared Library 0.6.0 in
  requirements.txt and setup.py.


## 0.6.0 - 2023-05-24

### Changed

- Parse DDI-C files with relPubl/citation that do not contain
  titlStmt/titl child. These files will result in a study without any
  related publications. (Implements
  [#27](https://github.com/cessda/cessda.cdc.aggregator.client/issues/27))

- Update dependencies:

  - Require Kuha Common 2.2.0 in requirements.txt and setup.py.


## 0.5.0 - 2022-11-21

### Added

- Support grant and funding information and related publication
  identifiers for studies. (Implements
  [#23](https://bitbucket.org/cessda/cessda.cdc.aggregator.client/issues/23))

### Changed

- Update dependencies:

  - Require Aggregator Shared Library 0.5.0 in requirements.txt and
    setup.py.
  - Require Kuha Common 2.0.1 in requirements.txt and setup.py.
  - Require Kuha Client 1.2.1 in requirements.txt and setup.py.
  - Require Tornado 6.2.0 in requirements.txt.

### Fixed

- Read DDI-Codebook XML from
  ``/codeBook/stdyDscr/stdyInfo/sumDscr/anlyUnit/concept/@vocabURI``
  and
  ``/codeBook/stdyDscr/method/dataColl/collMode/concept/@vocabURI``
  correctly.

**Note:** After upgrade the file-cache should be removed to make sure
all files are re-read and saved to Document Store.


## 0.4.0 - 2022-06-29

### Added

- Support reading DDI 3.3 for study level metadata. (Implements
  [#22](https://bitbucket.org/cessda/cessda.cdc.aggregator.client/issues/22))

### Changed

- Require Aggregator Shared Library 0.4.0 or newer at setup.py.
- Require Kuha Common 1.1.0 or newer at setup.py.
- Require Kuha Client 1.1.0 or newer at setup.py.
- Update dependecies at requirements.txt

  - Aggregator Shared Library 0.4.0
  - Kuha Common 1.1.0
  - Kuha Client 1.1.0


## 0.3.0 - 2022-05-18
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6577779.svg)](https://doi.org/10.5281/zenodo.6577779)

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
