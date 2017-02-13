# Notice

This is prerelease software, not yet suitable for production use.  Proceed at your own risk.

# Steem Blockchain Data Service

## Quickstart

`sbds` is available on Docker Hub as `steemit/sbds`.

e.g.

`docker run -d steemit/sbds`

## Overview

Stack: Python 3, SQLAlchemy, bottle.

`sbds` is a set of tool for querying the data of the Steem Blockchain. 

While providing direct interfaces to several pluggable storage architectures that may be used for querying the blockchain, `sbds` may also be used as a lower level API upon which other applications can be built.

## Architecture

The system has three conceptual functions:

1. Interfacing with a `steemd` instance to provide access to blocks, ranges of blocks, or the continual stream of
blocks as they are published on the blockchain.

2. Ingest, prepare, store, and index blocks in one of 3 storage backends (S3, SQL Database, and/or Elasticsearch).

3. Querying indexed blocks.

## Install

`sbds` is an installable python 3 package, though it is currently not published on pipy, and must be installed using git:

`pip3 install -e git+git@github.com:steemit/sbds.git#egg=sbds`

Installation will (during early development) require mysql and postgres development sources in order to build
correctly. As an alternative to installing those libraries, a `Dockerfile` is available.

## Usage

On initial use, blocks can be quickly loaded from "checkpoints" which are gzipped text files that are 1M
blocks in length and currently hosted on S3 at `s3://steemit-dev-sbds-checkpoints`.

Once the storage is synced with all previous blocks, blocks can be streamed to storage backends as they are confirmed.

These blocks are not cryptographically assured in any way (and `sbds` does not provide any cryptographic guarantees
or verify blockchain consensus state), so you may wish to regenerate these checkpoints.

`sbds` is designed to always be used in conjunction with a trusted instance of `steemd` to validate all block data before
`sbds` ever receives it.  This daemon **does not** implement any consensus rules.

### Command

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



#### Storages


##### S3
##### Command: `s3`

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


#### SQL Database


#### Data Model
```mysql
CREATE TABLE sbds_core_blocks
(
    raw TEXT,
    block_num INT(11) PRIMARY KEY NOT NULL,
    previous VARCHAR(50),
    timestamp TIMESTAMP,
    witness VARCHAR(50),
    witness_signature VARCHAR(150),
    transaction_merkle_root VARCHAR(50)
);
CREATE INDEX ix_sbds_core_blocks_timestamp ON sbds_core_blocks (timestamp);
CREATE INDEX ix_sbds_core_blocks_raw_fulltext ON sbds_core_blocks (raw);
CREATE TABLE sbds_core_transactions
(
    tx_id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
    block_num INT(11) NOT NULL,
    transaction_num SMALLINT(6) NOT NULL,
    ref_block_num INT(11) NOT NULL,
    ref_block_prefix BIGINT(20) NOT NULL,
    expiration TIMESTAMP NOT NULL,
    type ENUM('account_create', 'account_update', 'account_witness_proxy', 'account_witness_vote', 'cancel_transfer_from_savings', 'challenge_authority', 'change_recovery_account', 'comment', 'comment_options', 'convert', 'custom', 'custom_binary_operation', 'custom_json', 'decline_voting_rights_operation', 'delete_comment', 'escrow_approve', 'escrow_dispute', 'escrow_release', 'escrow_transfer', 'feed_publish', 'limit_order_cancel', 'limit_order_create', 'limit_order_create2', 'pow', 'pow2', 'prove_authority', 'recover_account', 'report_over_production', 'request_account_recovery', 'reset_account_operation', 'set_reset_account_operation', 'set_withdraw_vesting_route', 'transfer', 'transfer_from_savings', 'transfer_to_savings', 'transfer_to_vesting', 'vote', 'withdraw_vesting', 'witness_update') NOT NULL,
    CONSTRAINT sbds_core_transactions_ibfk_1 FOREIGN KEY (block_num) REFERENCES sbds_core_blocks (block_num) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX ix_sbds_core_transactions_type ON sbds_core_transactions (type);
CREATE UNIQUE INDEX sbds_ix_transactions ON sbds_core_transactions (block_num, transaction_num);
CREATE TABLE sbds_syn_accounts
(
    name VARCHAR(100) PRIMARY KEY NOT NULL,
    json_metadata TEXT,
    created DATETIME,
    post_count INT(11),
    comment_count INT(11),
    cast_vote_count INT(11),
    received_vote_count INT(11),
    witness_vote_count INT(11)
);
CREATE TABLE sbds_syn_images
(
    id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `_url` VARCHAR(250),
    inline TINYINT(1),
    inline_data TEXT,
    pac_id INT(11),
    extraction_source ENUM('body', 'meta'),
    CONSTRAINT sbds_syn_images_ibfk_1 FOREIGN KEY (pac_id) REFERENCES sbds_syn_posts_and_comments (id)
);
CREATE INDEX ix_sbds_syn_images__url ON sbds_syn_images (`_url`);
CREATE INDEX pac_id ON sbds_syn_images (pac_id);
CREATE TABLE sbds_syn_links
(
    id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `_url` VARCHAR(250),
    pac_id INT(11),
    extraction_source ENUM('body', 'meta') NOT NULL,
    body_offset INT(11),
    CONSTRAINT sbds_syn_links_ibfk_1 FOREIGN KEY (pac_id) REFERENCES sbds_syn_posts_and_comments (id)
);
CREATE INDEX ix_sbds_syn_links__url ON sbds_syn_links (`_url`);
CREATE INDEX pac_id ON sbds_syn_links (pac_id);
CREATE TABLE sbds_syn_posts_and_comments
(
    id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
    block_num INT(11) NOT NULL,
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    author_name VARCHAR(100) NOT NULL,
    parent_id INT(11),
    timestamp DATETIME,
    type ENUM('post', 'comment') NOT NULL,
    permlink VARCHAR(512) NOT NULL,
    title VARCHAR(250),
    body TEXT,
    json_metadata TEXT,
    category VARCHAR(300),
    url VARCHAR(500),
    length INT(11),
    language VARCHAR(40),
    has_patch TINYINT(1),
    CONSTRAINT ix_sbds_syn_posts_and_comments_ibfk_4 FOREIGN KEY (block_num, transaction_num, operation_num) REFERENCES sbds_tx_comments (block_num, transaction_num, operation_num),
    CONSTRAINT sbds_syn_posts_and_comments_ibfk_1 FOREIGN KEY (author_name) REFERENCES sbds_syn_accounts (name),
    CONSTRAINT sbds_syn_posts_and_comments_ibfk_2 FOREIGN KEY (parent_id) REFERENCES sbds_syn_posts_and_comments (id)
);
CREATE INDEX ix_sbds_syn_posts_and_comments_author_name ON sbds_syn_posts_and_comments (author_name);
CREATE INDEX ix_sbds_syn_posts_and_comments_body_fulltext ON sbds_syn_posts_and_comments (body);
CREATE INDEX ix_sbds_syn_posts_and_comments_parent_id ON sbds_syn_posts_and_comments (parent_id);
CREATE INDEX ix_sbds_syn_posts_and_comments_permlink ON sbds_syn_posts_and_comments (permlink);
CREATE UNIQUE INDEX ix_sbds_syn_posts_and_comments_unique_1 ON sbds_syn_posts_and_comments (block_num, transaction_num, operation_num);
CREATE TABLE sbds_syn_tag_table
(
    post_and_comment_id INT(11) NOT NULL,
    tag_id VARCHAR(50) NOT NULL,
    CONSTRAINT sbds_syn_tag_table_ibfk_1 FOREIGN KEY (post_and_comment_id) REFERENCES sbds_syn_posts_and_comments (id),
    CONSTRAINT sbds_syn_tag_table_ibfk_2 FOREIGN KEY (tag_id) REFERENCES sbds_syn_tags (`_id`)
);
CREATE INDEX post_and_comment_id ON sbds_syn_tag_table (post_and_comment_id);
CREATE INDEX tag_id ON sbds_syn_tag_table (tag_id);
CREATE TABLE sbds_syn_tags
(
    `_id` VARCHAR(50) PRIMARY KEY NOT NULL
);
CREATE TABLE sbds_tx_account_creates
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    fee DECIMAL(15,4) NOT NULL,
    creator VARCHAR(50) NOT NULL,
    new_account_name VARCHAR(50),
    owner_key VARCHAR(80) NOT NULL,
    active_key VARCHAR(80) NOT NULL,
    posting_key VARCHAR(80) NOT NULL,
    memo_key VARCHAR(250) NOT NULL,
    json_metadata TEXT,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('account_create') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_account_creates_creator ON sbds_tx_account_creates (creator);
CREATE INDEX ix_sbds_tx_account_creates_operation_type ON sbds_tx_account_creates (operation_type);
CREATE INDEX ix_sbds_tx_account_creates_timestamp ON sbds_tx_account_creates (timestamp);
CREATE TABLE sbds_tx_account_recovers
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    recovery_account VARCHAR(50),
    account_to_recover VARCHAR(50) NOT NULL,
    recovered TINYINT(1),
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('request_account_recovery', 'recover_account') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_account_recovers_operation_type ON sbds_tx_account_recovers (operation_type);
CREATE INDEX ix_sbds_tx_account_recovers_timestamp ON sbds_tx_account_recovers (timestamp);
CREATE TABLE sbds_tx_account_updates
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    account VARCHAR(50),
    key_auth1 VARCHAR(80),
    key_auth2 VARCHAR(80),
    memo_key VARCHAR(250),
    json_metadata TEXT,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('account_update', 'change_recovery_account') NOT NULL,
    account_to_recover VARCHAR(50),
    new_recovery_account VARCHAR(50),
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_account_updates_operation_type ON sbds_tx_account_updates (operation_type);
CREATE INDEX ix_sbds_tx_account_updates_timestamp ON sbds_tx_account_updates (timestamp);
CREATE TABLE sbds_tx_account_witness_proxies
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    account VARCHAR(50) NOT NULL,
    Proxy VARCHAR(50) NOT NULL,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('account_witness_proxy') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_account_witness_proxies_operation_type ON sbds_tx_account_witness_proxies (operation_type);
CREATE INDEX ix_sbds_tx_account_witness_proxies_timestamp ON sbds_tx_account_witness_proxies (timestamp);
CREATE TABLE sbds_tx_account_witness_votes
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    account VARCHAR(50) NOT NULL,
    witness VARCHAR(50) NOT NULL,
    approve TINYINT(1),
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('account_witness_vote') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_account_witness_votes_operation_type ON sbds_tx_account_witness_votes (operation_type);
CREATE INDEX ix_sbds_tx_account_witness_votes_timestamp ON sbds_tx_account_witness_votes (timestamp);
CREATE TABLE sbds_tx_comments
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    author VARCHAR(50) NOT NULL,
    permlink VARCHAR(512) NOT NULL,
    parent_author VARCHAR(50),
    parent_permlink VARCHAR(512),
    title VARCHAR(250),
    body TEXT,
    json_metadata TEXT,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('comment') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_comments_author ON sbds_tx_comments (author);
CREATE INDEX ix_sbds_tx_comments_permlink ON sbds_tx_comments (permlink);
CREATE INDEX ix_sbds_tx_comments_operation_type ON sbds_tx_comments (operation_type);
CREATE INDEX ix_sbds_tx_comments_timestamp ON sbds_tx_comments (timestamp);
CREATE TABLE sbds_tx_comments_options
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    author VARCHAR(50) NOT NULL,
    permlink VARCHAR(512) NOT NULL,
    max_accepted_payout DECIMAL(15,4) NOT NULL,
    percent_steem_dollars SMALLINT(6),
    allow_votes TINYINT(1) NOT NULL,
    allow_curation_rewards TINYINT(1) NOT NULL,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('comment_options') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_comments_options_operation_type ON sbds_tx_comments_options (operation_type);
CREATE INDEX ix_sbds_tx_comments_options_timestamp ON sbds_tx_comments_options (timestamp);
CREATE TABLE sbds_tx_converts
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    owner VARCHAR(50) NOT NULL,
    requestid BIGINT(20) NOT NULL,
    amount DECIMAL(15,4) NOT NULL,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('convert') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_converts_operation_type ON sbds_tx_converts (operation_type);
CREATE INDEX ix_sbds_tx_converts_timestamp ON sbds_tx_converts (timestamp);
CREATE TABLE sbds_tx_customs
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    tid VARCHAR(50) NOT NULL,
    json_metadata TEXT,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('custom_json', 'custom') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_customs_operation_type ON sbds_tx_customs (operation_type);
CREATE INDEX ix_sbds_tx_customs_timestamp ON sbds_tx_customs (timestamp);
CREATE TABLE sbds_tx_delete_comments
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    author VARCHAR(50) NOT NULL,
    permlink VARCHAR(250) NOT NULL,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('delete_comment') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_delete_comments_operation_type ON sbds_tx_delete_comments (operation_type);
CREATE INDEX ix_sbds_tx_delete_comments_timestamp ON sbds_tx_delete_comments (timestamp);
CREATE TABLE sbds_tx_feeds
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    publisher VARCHAR(50) NOT NULL,
    exchange_rate_base DECIMAL(15,4) NOT NULL,
    exchange_rate_quote DECIMAL(15,4) NOT NULL,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('feed_publish') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_feeds_operation_type ON sbds_tx_feeds (operation_type);
CREATE INDEX ix_sbds_tx_feeds_timestamp ON sbds_tx_feeds (timestamp);
CREATE TABLE sbds_tx_limit_orders
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    owner VARCHAR(50) NOT NULL,
    orderid BIGINT(20) NOT NULL,
    cancel TINYINT(1),
    amount_to_sell DECIMAL(15,4),
    min_to_receive DECIMAL(15,4),
    fill_or_kill TINYINT(1),
    expiration DATETIME,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('limit_order_cancel', 'limit_order_create') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_limit_orders_operation_type ON sbds_tx_limit_orders (operation_type);
CREATE INDEX ix_sbds_tx_limit_orders_timestamp ON sbds_tx_limit_orders (timestamp);
CREATE TABLE sbds_tx_pows
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    worker_account VARCHAR(50) NOT NULL,
    block_id VARCHAR(40) NOT NULL,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('pow2', 'pow') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_pows_worker_account ON sbds_tx_pows (worker_account);
CREATE INDEX ix_sbds_tx_pows_operation_type ON sbds_tx_pows (operation_type);
CREATE INDEX ix_sbds_tx_pows_timestamp ON sbds_tx_pows (timestamp);
CREATE TABLE sbds_tx_transfers
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    type VARCHAR(50) NOT NULL,
    `from` VARCHAR(50),
    `to` VARCHAR(50),
    amount DECIMAL(15,4),
    amount_symbol VARCHAR(5),
    memo VARCHAR(250),
    request_id INT(11),
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('cancel_transfer_from_savings', 'transfer_to_vesting', 'transfer_from_savings', 'transfer', 'transfer_to_savings') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_transfers_from ON sbds_tx_transfers (`from`);
CREATE INDEX ix_sbds_tx_transfers_to ON sbds_tx_transfers (`to`);
CREATE INDEX ix_sbds_tx_transfers_type ON sbds_tx_transfers (type);
CREATE INDEX ix_sbds_tx_transfers_operation_type ON sbds_tx_transfers (operation_type);
CREATE INDEX ix_sbds_tx_transfers_timestamp ON sbds_tx_transfers (timestamp);
CREATE TABLE sbds_tx_votes
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    voter VARCHAR(50) NOT NULL,
    author VARCHAR(50) NOT NULL,
    permlink VARCHAR(512) NOT NULL,
    weight INT(11),
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('vote') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_votes_author ON sbds_tx_votes (author);
CREATE INDEX ix_sbds_tx_votes_voter ON sbds_tx_votes (voter);
CREATE INDEX ix_sbds_tx_votes_operation_type ON sbds_tx_votes (operation_type);
CREATE INDEX ix_sbds_tx_votes_timestamp ON sbds_tx_votes (timestamp);
CREATE TABLE sbds_tx_withdraw_vesting_routes
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    from_account VARCHAR(50) NOT NULL,
    to_account VARCHAR(50) NOT NULL,
    percent SMALLINT(6) NOT NULL,
    auto_vest TINYINT(1),
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('set_withdraw_vesting_route') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_withdraw_vesting_routes_operation_type ON sbds_tx_withdraw_vesting_routes (operation_type);
CREATE INDEX ix_sbds_tx_withdraw_vesting_routes_timestamp ON sbds_tx_withdraw_vesting_routes (timestamp);
CREATE TABLE sbds_tx_withdraws
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    account VARCHAR(50) NOT NULL,
    vesting_shares DECIMAL(15,4) NOT NULL,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('withdraw_vesting') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_withdraws_operation_type ON sbds_tx_withdraws (operation_type);
CREATE INDEX ix_sbds_tx_withdraws_timestamp ON sbds_tx_withdraws (timestamp);
CREATE TABLE sbds_tx_witness_updates
(
    transaction_num SMALLINT(6) NOT NULL,
    operation_num SMALLINT(6) NOT NULL,
    owner VARCHAR(50) NOT NULL,
    url VARCHAR(250) NOT NULL,
    block_signing_key VARCHAR(64) NOT NULL,
    props_account_creation_fee DECIMAL(15,4) NOT NULL,
    props_maximum_block_size INT(11) NOT NULL,
    props_sbd_interest_rate INT(11) NOT NULL,
    fee DECIMAL(15,4) NOT NULL,
    block_num INT(11) NOT NULL,
    timestamp TIMESTAMP,
    operation_type ENUM('witness_update') NOT NULL,
    CONSTRAINT `PRIMARY` PRIMARY KEY (block_num, transaction_num, operation_num)
);
CREATE INDEX ix_sbds_tx_witness_updates_operation_type ON sbds_tx_witness_updates (operation_type);
CREATE INDEX ix_sbds_tx_witness_updates_timestamp ON sbds_tx_witness_updates (timestamp);

```

#### Command: `db`
 
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

