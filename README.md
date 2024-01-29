# Nextline RDB

[![PyPI - Version](https://img.shields.io/pypi/v/nextline-rdb.svg)](https://pypi.org/project/nextline-rdb)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nextline-rdb.svg)](https://pypi.org/project/nextline-rdb)
[![Test Status](https://github.com/simonsobs/nextline-rdb/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-rdb/actions/workflows/unit-test.yml)
[![Test Status](https://github.com/simonsobs/nextline-rdb/actions/workflows/type-check.yml/badge.svg)](https://github.com/simonsobs/nextline-rdb/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/simonsobs/nextline-rdb/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-rdb)

A plugin for [nextline-graphql](https://github.com/simonsobs/nextline-graphql)

---

**Table of Contents**

- [Nextline RDB](#nextline-rdb)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [License](#license)
  - [Contact](#contact)

## Installation

```console
pip install nextline-rdb
```

## Configuration

| Environment variable | Default value         | Description                                                                                   |
| -------------------- | --------------------- | --------------------------------------------------------------------------------------------- |
| `NEXTLINE_DB__URL`   | `sqlite+aiosqlite://` | The [DB URL](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) of SQLAlchemy |

## License

- _Nextline RDB_ is licensed under the [MIT](https://spdx.org/licenses/MIT.html) license.

## Contact

- [Tai Sakuma](https://github.com/TaiSakuma) <span itemscope itemtype="https://schema.org/Person"><a itemprop="sameAs" content="https://orcid.org/0000-0003-3225-9861" href="https://orcid.org/0000-0003-3225-9861" target="orcid.widget" rel="me noopener noreferrer" style="vertical-align:text-top;"><img src="https://orcid.org/sites/default/files/images/orcid_16x16.png" style="width:1em;margin-right:.5em;" alt="ORCID iD icon"></a></span>
