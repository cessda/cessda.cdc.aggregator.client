# CESSDA CDC Aggregator - Client #

[![Build Status](https://jenkins.cessda.eu/buildStatus/icon?job=cessda.cdc.aggregator.client%2Fmaster)](https://jenkins.cessda.eu/job/cessda.cdc.aggregator.client/job/master/)
[![Bugs](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=bugs)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Code Smells](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=code_smells)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Coverage](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=coverage)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Duplicated Lines (%)](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=duplicated_lines_density)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Lines of Code](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=ncloc)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Maintainability Rating](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=sqale_rating)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Quality Gate Status](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=alert_status)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Reliability Rating](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=reliability_rating)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Security Rating](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=security_rating)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Technical Debt](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=sqale_index)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)
[![Vulnerabilities](https://sonarqube.cessda.eu/api/project_badges/measure?project=cessda.cdc.aggregator.client&metric=vulnerabilities)](https://sonarqube.cessda.eu/dashboard?id=cessda.cdc.aggregator.client)

Command line client for synchronizing records to CESSDA CDC Aggregator
DocStore. This program is part of CESSDA CDC Aggregator.

## Installation ##

```sh
python3 -m venv cdcagg-env
source cdcagg-env/bin/activate
cd cessda.cdc.aggregator.client
pip install -r requirements.txt
pip install .
```


## Run ##

Change <docstore-url> to CDC Aggregator DocStore server URL. Change
<xml-sources> to a path pointing to a folder containing files to
synchronize.

```sh
python -m cdcagg_client.sync --document-store-url <docstore-url> --file-cache file_cache.pickle <xml-sources>
```

## Configuration reference ##

```sh
python -m cdcagg_client.sync --help
```


## License ##

See the [LICENSE](LICENSE.txt) file.
