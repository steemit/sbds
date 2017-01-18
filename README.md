# SBDS (Steem Block Data Service)
## Overview
SBDS refers generally to the collection of tool, utilities, and services designed to allow querying the Steemit blockchain. 

While providing direct interfaces to several pluggable storage architectures that may be used for querying the blockchain, SBDS may also be used as a lower level API upon which other application can be built.

## Architecture
The system has three conceptual functions

1. Interfacing with a `steemd` instance to provide access to blocks, ranges of blocks, or the continual stream of blocks as they are published on the blockchain

2. Ingest, prepare, store, and index blocks in one of 3 storage backends (S3, Postgres, Elasticsearch)

3. Querying indexed blocks

## Install
SBDS is an installable python 3 package, though it is currently not published on pipy, and must be installed using git:

```pip3 install -e git+git@github.com:steemit/sbds.git#egg=sbds```

Installation will (during early development) require mysql and postgres development sources in order to build correctly. As an alternative to installing those libraries, a `Dockerfile` is available.


## Usage

During an initial install, blocks can be quickly loaded from "checkpoints" which are gzipped text files that are 1M blocks in length and currently hosted on S3 at `s3://steemit-dev-sbds-checkpoints`.

Once the storage is synced with all previous blocks, blocks can be streamed to storage backends as they are confirmed.

### Streaming / Blockchain Commands

#### `sbds`

```
$ sbds --help
Usage: sbds [OPTIONS]

  Output blocks from steemd in JSON format.

  Which Steemd:
  
  1. CLI "--server" option if provided
  2. ENV var "WEBSOCKET_URL" if provided
  3. Default: "wss://steemit.com/wspa"

  Which Blocks To Output:
  
  - Stream blocks beginning with current block by omitting --start, --end, and BLOCKS
  - Fetch a range of blocks using --start and/or --end
  - Fetch list of blocks by passing BLOCKS a JSON array of block numbers (either filename or "-" for STDIN)

  Where To Output Blocks:

  2. ENV var "BLOCKS_OUT" if provided
  3. Default: STDOUT

Options:
  --server WEBSOCKET_URL     Steemd server URL
  --block_nums FILENAME
  --start INTEGER BLOCK_NUM  Starting block_num, default is 1
  --end INTEGER BLOCK_NUM    Ending block_num, default is infinity
  --help                     Show this message and exit.
```

#### `notify`
```
$ notify --help
Usage: notify [OPTIONS] [BLOCKS]

wsdump.py --text '{"jsonrpc": "2.0", "method": "call", "params": ["database_api","set_block_applied_callback",[1234]], "id": 1}' --raw
wss://steemit.com/wspa | notify

Options:
  --help  Show this message and exit.

```


#### `block-height`
```
$ block-height --help
Usage: block-height [OPTIONS]

Options:
  --url STEEMD_HTTP_URL  Steemd HTTP server URL
  --help                 Show this message and exit.

```
#### `bulk-blocks`
```
$ bulk-blocks --help
Usage: bulk-blocks [OPTIONS]

  Quickly request blocks from steemd

Options:
  --start INTEGER
  --end INTEGER
  --chunksize INTEGER
  --max_workers INTEGER
  --url STEEMD_HTTP_URL  Steemd HTTP server URL
  --help                 Show this message and exit.

```

#### `load-checkpoint-blocks`
```
$ load-checkpoint-blocks --help
Usage: load-checkpoint-blocks [OPTIONS] CHECKPOINTS_DIR

  Load blocks from locally stored "checkpoint" files

Options:
  --start INTEGER
  --end INTEGER
  --help           Show this message and exit.

```

#### Storage Commands

#### `s3`

```
$ s3 --help
Usage: s3 [OPTIONS] COMMAND [ARGS]...

  This command provides AWS S3 steem block storage. 
  
  s3 create-bucket <bucket name>
  
  or
  
  sbds --start 1 | s3 put-json-blocks <bucket-name> -

Options:
  --help  Show this message and exit.

Commands:
  create-bucket
  put-json-blocks

```

#### `es`

```
$ es --help
Usage: es [OPTIONS] COMMAND [ARGS]...

  Group of commands used to interact with the elasticsearch storage backend.
  Typical usage would be reading blocks in JSON format from STDIN and then
  storing those blocks in the index:

  sbds | es insert-blocks

  In the example above, the "sbds" command streams new blocks to STDOUT,
  which are piped to STDIN of the "insert-blocks" db command by default. The
  "database_url" was read from the "DATABASE_URL" ENV var, though it may
  optionally be provided on the command line:

  db --elasticsearch_url 'http[s]://user:password@host/index[?key=value..]' test

Options:
  --elasticsearch_url TEXT  Elastic connection URL, read from
                            "ELASTICSEARCH_URL" ENV var by default
  --index TEXT
  --help                    Show this message and exit.

Commands:
  init                Create any missing mappings on the index
  insert-blocks       Insert or update blocks in the index, accepts...
  insert-bulk-blocks  Insert or update blocks in the index, accepts...
  reset               Drop and then create the index and mappings
  test                Test connection to elasticsearch

```


#### `db`
 
```
$ db --help
Usage: db [OPTIONS] COMMAND [ARGS]...

  Group of commands used to interact with the SQL storage backend. Typical
  usage would be reading blocks in JSON format from STDIN and then storing
  those blocks in the database:

  sbds | db insert-blocks

  In the example above, the "sbds" command streams new blocks to STDOUT,
  which are piped to STDIN of the "db insert-blocks" command by default. The
  "database_url" was read from the "DATABASE_URL" ENV var, though it may
  optionally be provided on the command line:

  db --database_url 'dialect[+driver]://user:password@host/dbname[?key=value..]' test

Options:
  --database_url TEXT  Database connection URL in RFC-1738 format, read from
                       "DATABASE_URL" ENV var by default
  --echo / --no-echo   Enable(default)/disable the echoing of SQL commands
                       issued to database
  --help               Show this message and exit.

Commands:
  add-blocks-fast        Insert or update transactions in the...
  add-operations-fast    Insert or update transactions in the...
  add-transactions-fast  Insert or update transactions in the...
  init                   Create any missing tables on the database
  insert-blocks          Insert or update blocks in the database,...
  insert-transactions    Insert or update transactions in the...
  last-block             Create any missing tables on the database
  reset                  Drop and then create tables on the database
  test                   Test connection to database


```
##### Docker Command To Stream Blocks To DB Storage
```
docker run --rm \
    --env 'DATABASE_URL=sqlite:///local.db' \
    --env 'WEBSOCKET_URL=wss://steemit.com/wspa' \
    --name sbds-blocks \
    steemit/sbds sbds-populate.sh

```


### Querying / Reporting

#### Docker Command To Run HTTP Server
```
docker run --rm \
    --env 'DATABASE_URL=sqlite:///local.db' \
    --env 'WEBSOCKET_URL=wss://steemit.com/wspa' \
    --publish 127.0.0.1:8080:8080 \
    --name sbds-web \
    steemit/sbds dev-server 
```

