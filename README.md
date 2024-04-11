# ISCC - Software Development Kit

[![Build](https://github.com/iscc/iscc-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/iscc/iscc-sdk/actions/workflows/ci.yml)
[![Version](https://img.shields.io/pypi/v/iscc-sdk.svg)](https://pypi.python.org/pypi/iscc-sdk/)
[![Coverage](https://codecov.io/gh/iscc/iscc-sdk/branch/main/graph/badge.svg?token=7BJ7HJU815)](https://codecov.io/gh/iscc/iscc-sdk)
[![Quality](https://app.codacy.com/project/badge/Grade/aa791abf9d824f6aa65a8f86b9222c90)](https://www.codacy.com/gh/iscc/iscc-sdk/dashboard)
[![Downloads](https://pepy.tech/badge/iscc-sdk)](https://pepy.tech/project/iscc-sdk)

`iscc-sdk` is a Python development kit for creating and managing [ISCC](https://core.iscc.codes)
(*International Standard Content Code*)

## What is an ISCC

The ISCC is a similarity preserving identifier for digital media assets.

ISCCs are generated algorithmically from digital content, just like cryptographic hashes. However,
instead of using a single cryptographic hash function to identify data only, the ISCC uses various
algorithms to create a composite identifier that exhibits similarity-preserving properties (soft
hash).

The component-based structure of the ISCC identifies content at multiple levels of abstraction. Each
component is self-describing, modular, and can be used separately or with others to aid in various
content identification tasks. The algorithmic design supports content deduplication, database
synchronization, indexing, integrity verification, timestamping, versioning, data provenance,
similarity clustering, anomaly detection, usage tracking, allocation of royalties, fact-checking and
general digital asset management use-cases.

## What is `iscc-sdk`

`iscc-sdk` is built on top of `iscc-core` and adds high level features for generating and handling
ISCC codes for all the different mediatypes:

- mediatype detection
- metadata extraction and embedding
- mediatype specific content extraction and pre-processing
- iscc indexing and search

## Requirements

Python 3.8 to 3.11 on 64-bit systems

## Installation

Use the Python package manager [pip](https://pip.pypa.io/en/stable/) to install `iscc-sdk`.

```bash
pip install iscc-sdk
```

## Getting Started

Create an ISCC-CODE for a media file:

```python
import iscc_sdk as idk

print(idk.code_iscc("/path/to/mediafile.jpg"))
```

Using the CLI tool to create an ISCC-CODE

```shell
idk create /path/to/mediafile.jpg
```

Batch creation of ISCC-CODEs

```shell
idk batch /folder_with_media_files
```

## Documentation

<https://sdk.iscc.codes>

## Troubleshooting

On Linux and MacOS you might need to install taglib as a prerequisite. On Ubuntu, Mint and other
Debian-Based distributions do:

```shell
sudo apt install libtag1-dev
```

On a Mac, use HomeBrew:

```shell
brew install taglib
```

## Project Status

The ISCC has been accepted by ISO as full work item ISO/AWI 24138 - International Standard Content
Code and is currently being standardized at TC 46/SC 9/WG 18.
https://www.iso.org/standard/77899.html

!!! attention
    The `iscc-sdk` library and the accompanying documentation is under development. API changes and
    other backward incompatible changes are to be expected until the upcoming v1.0 stable release.

## Maintainers

[@titusz](https://github.com/titusz)

## Contributing

Pull requests are welcome. For significant changes, please open an issue first to discuss your
plans. Please make sure to update tests as appropriate.

You may also want join our developer chat on Telegram at <https://t.me/iscc_dev>.
