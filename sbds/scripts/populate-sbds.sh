#!/bin/bash
#
# Load blocks and transactions from steemd into database

# confirm required environment vars are set



command_exists() {
  hash "$1" 2>/dev/null && return 0 || return 1
}

is_interactive() {
  local fd=0 # stdin
  if [[ -t "$fd" || -p /dev/stdin ]]; then
    return 0
  else
    return 1
  fi
}

interactive_block_load() {
  local LATEST_CHAIN_BLOCK=$(block-height)
  test_var_is_test="${LATEST_CHAIN_BLOCK:?Need to set LATEST_CHAIN_BLOCK non-empty}"

  local LATEST_DB_BLOCK="$(db --database_url "${DATABASE_URL}" last-block)"
  if [[ ${LATEST_DB_BLOCK} -lt 1 ]]; then
    local LATEST_DB_BLOCK=1
  fi
  local DB_HOST=$(python -c 'import sys, urllib.parse; print(urllib.parse.urlparse(sys.argv[1]).hostname)' ${DATABASE_URL})
  local STEEMD_HOST=$(python -c 'import sys, urllib.parse; print(urllib.parse.urlparse(sys.argv[1]).hostname)' ${WEBSOCKET_URL})
  local BLOCKS_TO_ADD=$((${LATEST_CHAIN_BLOCK} - ${LATEST_DB_BLOCK}))
  local PV_OPTS="--progress --rate --eta --timer --average-rate --line-mode --size ${BLOCKS_TO_ADD} --name blocks"
  cat <<- EOF

Populating SBDS Database

Job Details
========================
steemd block source host:       ${STEEMD_HOST}
database host:                  ${DB_HOST}
latest database block_num:      ${LATEST_DB_BLOCK}
latest blockchain block_num:    ${LATEST_CHAIN_BLOCK}
approximate blocks to add:      ${BLOCKS_TO_ADD}

Loading blocks...
EOF

  bulk-blocks --start ${LATEST_DB_BLOCK} --end ${LATEST_CHAIN_BLOCK}  \
    | pv ${PV_OPTS}  \
    | tee  \
      >( db --database_url "${DATABASE_URL}" insert-blocks )  \
      >( db --database_url "${DATABASE_URL}" insert-transactions )  \
      >/dev/null

  local LATEST_DB_BLOCK=$(db --database_url "${DATABASE_URL}" last-block)
  sbds --start ${LATEST_DB_BLOCK}  \
    | tee  \
      >( db --database_url "${DATABASE_URL}" insert-blocks )  \
      >( db --database_url "${DATABASE_URL}" insert-transactions )  \
      >/dev/null
}

block_load() {
  local LATEST_DB_BLOCK="$(db --database_url "${DATABASE_URL}" last-block)"
  if [[ ${LATEST_DB_BLOCK} -lt 1 ]]; then
    local LATEST_DB_BLOCK=1
  fi

  local LATEST_DB_BLOCK=$(db --database_url "${DATABASE_URL}" last-block)
  sbds --start ${LATEST_DB_BLOCK}  \
    | tee  \
    >( db --database_url "${DATABASE_URL}" insert-blocks )  \
    >( db --database_url "${DATABASE_URL}" insert-transactions )  \
    >/dev/null
}


main () {
  # confirm required environment vars are set
  local test_var_is_test="${DATABASE_URL:?Need to set DATABASE_URL non-empty}"
  local test_var_is_test="${WEBSOCKET_URL:?Need to set WEBSOCKET_URL non-empty}"

  if command_exists pv && is_interactive; then
    echo "Loading blocks interactively..."
    set -e
    interactive_block_load;
  else
    set -e
    block_load;
  fi
}

main "$@"