# deep-oc-client

[![GitHub license](https://img.shields.io/github/license/deephdc/deep-oc-client.svg)](https://github.com/deephdc/deep-oc-client/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/release/deephdc/deep-oc-client.svg)](https://github.com/deephdc/deep-oc-client/releases)
[![PyPI](https://img.shields.io/pypi/v/deep-oc-client.svg)](https://pypi.python.org/pypi/deep-oc-client)
[![Python versions](https://img.shields.io/pypi/pyversions/deep-oc-client.svg)](https://pypi.python.org/pypi/deep-oc-client)
[![Build Status](https://jenkins.indigo-datacloud.eu/buildStatus/icon?job=Pipeline-as-code%2Fdeep-oc-client%2Fmaster)](https://jenkins.indigo-datacloud.eu/job/Pipeline-as-code/job/deep-oc-client/job/master/)

<img src="https://marketplace.deep-hybrid-datacloud.eu/images/logo-deep.png" width=200 alt="DEEP-Hybrid-DataCloud logo"/>

DEEP OC Command Line Interface (DEEP OC CLI).

This is a command line tool (and also a library) to interact with the
[DEEP-Hybrid-DataCloud Marketplace](https://marketplace.deep-hybrid-datacloud.eu/),
allowing you to browse, get information, download and execute the published
modules.

* Free software: Apache License 2.0
* Source: https://github.com/alvarolopez/deep-oc-client
* Bugs: https://github.com/alvarolopez/deep-oc-client/issues
* Documentation: TBD

## Installation

You can install it via PyPI:

    pip install deep-oc-client

## Usage

To list the modules you can use `module ls`:

    $ deep-oc module list
    +-------------------------------------------+-------------------------------------------------+--------------------------------------------------------------------+------------+
    | Title                                     | DockerHub container                             | url                                                                | License    |
    +-------------------------------------------+-------------------------------------------------+--------------------------------------------------------------------+------------+
    | DEEP OC Dogs breed detection              | deephdc/deep-oc-dogs_breed_det                  | https://github.com/deephdc/DEEP-OC-dogs_breed_det                  | MIT        |
    +-------------------------------------------+-------------------------------------------------+--------------------------------------------------------------------+------------+


To fetch information about a module you can use `module show`:

    $ deep-oc module show https://github.com/deephdc/deep-oc-dogs_breed_det
    +----------------------+---------------------------------------------------------------------------+
    | Field                | Value                                                                     |
    +----------------------+---------------------------------------------------------------------------+
    | TOSCA_template       | Yes                                                                       |
    | build_status         | SUCCESS                                                                   |
    | date_creation        | 2018-11-18                                                                |
    | docker_registry_repo | deephdc/deep-oc-dogs_breed_det                                            |
    | dockerfile_repo      | https://github.com/deephdc/DEEP-OC-dogs_breed_det                         |
    | keywords             | ['docker', 'tensorflow', 'cnn']                                           |
    | license              | MIT                                                                       |
    | model_source_code    | https://github.com/deephdc/dogs_breed_det                                 |
    | summary              | A test application to identify Dog's breed as an example for DEEPaaS API. |
    | title                | DEEP OC Dogs breed detection                                              |
    +----------------------+---------------------------------------------------------------------------+

In order to get the complete list of commands, as well as usage details please
check the output of:

    deep-oc help
