# nextline-rdb

[![PyPI - Version](https://img.shields.io/pypi/v/nextline-rdb.svg)](https://pypi.org/project/nextline-rdb)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nextline-rdb.svg)](https://pypi.org/project/nextline-rdb)

[![Test Status](https://github.com/simonsobs/nextline-rdb/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-rdb/actions/workflows/unit-test.yml)
[![Test Status](https://github.com/simonsobs/nextline-rdb/actions/workflows/type-check.yml/badge.svg)](https://github.com/simonsobs/nextline-rdb/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/simonsobs/nextline-rdb/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-rdb)

A plugin for [nextline-graphql](https://github.com/simonsobs/nextline-graphql).
A relational database for nextline-graphql.

---

**Table of Contents**

- [Installation](#installation)
- [Configuration](#configuration)
- [Examples](#examples)

## Installation

```bash
pip install nextline-rdb
```

Nextline-graphql automatically detects this package as a plugin.

## Configuration

| Environment variable | Default value         | Description                                                                                   |
| -------------------- | --------------------- | --------------------------------------------------------------------------------------------- |
| `NEXTLINE_DB__URL`   | `sqlite+aiosqlite://` | The [DB URL](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) of SQLAlchemy |

**Note:** Only tested on SQLite + aiosqlite.

## Examples

### How to run Nextline-graphql with Nextline RDB

#### In a virtual environment

Create a virtual environment and install packages.

```bash
python -m venv venv
source venv/bin/activate
pip install nextline-graphql
pip install nextline-rdb
pip install uvicorn
```

Specify the database URL.

```bash
export NEXTLINE_DB__URL="sqlite+aiosqlite:///db.sqlite3"
```

Run on the port 8080.

```bash
uvicorn --lifespan on --factory --port 8080 nextlinegraphql:create_app
```

Check with a web browser at <http://localhost:8080/>.

#### In a Docker container

Create a Docker image.

```bash
git clone git@github.com:simonsobs/nextline-rdb.git
cd nextline-rdb
docker image build --tag nextline-rdb .
```

Run on the port 8080 with a file on the host machine `db/db.sqlite3` as the
persistent DB.
The directory `db/` and the file `db.sqlite3` will be created if
they don't exist.

```bash
docker run -p 8080:8000 --env NEXTLINE_DB__URL='sqlite+aiosqlite:////db/db.sqlite3' -v "$(pwd)/db:/db" nextline-rdb
```

Check with a web browser at <http://localhost:8080/>.
