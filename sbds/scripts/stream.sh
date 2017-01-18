#!/usr/bin/env bash
#
# Load block data from steemd into all database tables

# confirm required environment vars are set
test_var_is_test="${DATABASE_URL:?Need to set DATABASE_URL non-empty}"
test_var_is_test="${WEBSOCKET_URL:?Need to set WEBSOCKET_URL non-empty}"

LATEST_DB_BLOCK="$(db --database_url "${DATABASE_URL}" last-block)"

sbds --start "${STARTING_BLOCK_NUM:-$LATEST_DB_BLOCK}"  \
  | db --database_url "${DATABASE_URL}" insert-all
