# CESSDA Metadata Aggregator - Client #

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

Command line client for synchronizing records to CESSDA Metadata Aggregator
DocStore. This program is part of CESSDA Metadata Aggregator.

Source code is hosted at Bitbucket [https://bitbucket.org/cessda/cessda.cdc.aggregator.client](https://bitbucket.org/cessda/cessda.cdc.aggregator.client).


## Features ##

  - Synchronize a folder of XML files recursively to DocStore.
  - Keep a file-cache to speed-up consecutive syncronization runs.
  - Supports DDI 1.2.2, DDI 2.5 and DDI 3.1 XML files.


## Requirements ##

  - Python 3.8 or newer.
  - Running CESSDA Metadata Aggregator DocStore instance.


## Installation ##

On Ubuntu 20.04


### Get Package ###

Clone the repository using Git.

```sh
git clone https://bitbucket.org/cessda/cessda.cdc.aggregator.client.git
```

Or fetch a specific release using a tag. For example to get 0.2.0 release.

```sh
git clone --branch 0.2.0 https://bitbucket.org/cessda/cessda.cdc.aggregator.client.git
```


### Install Client ###

It is recommended to install packages inside Python virtual
environment to isolate the install. This package also provides a
Dockerfile to help setup a containerized environment.

Create the Python virtual environment and activate it.

```sh
python3 -m venv cdcagg-env
source cdcagg-env/bin/activate
```

Install Python packages.

```sh
cd cessda.cdc.aggregator.client
pip install -r requirements.txt
pip install .
```

To upgrade existing install, use ``--upgrade`` flag in pip commands. Pip
uses ``only-if-needed`` upgrade strategy by default since version
10.0.0, but for backwards compatibility the option is also included in
the example.

```sh
pip install --upgrade -r requirements.txt --upgrade-strategy=only-if-needed
pip install . --upgrade --upgrade-strategy=only-if-needed
```


## Run ##

Change ``<docstore-url>`` to CDC Aggregator DocStore server URL. Change
``<xml-sources>`` to a path pointing to a folder containing files to
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
