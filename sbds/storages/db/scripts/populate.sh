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


latest_db_block() {
  local LATEST_DB_BLOCK="$(db --database_url "${DATABASE_URL}" last-block)"
  if [[ ${LATEST_DB_BLOCK} -lt 1 ]]; then
    local LATEST_DB_BLOCK=1
  fi
  echo "${LATEST_DB_BLOCK}"
}

stream_blocks() {
  local LATEST_DB_BLOCK="$(latest_db_block)"
  sbds --start "${LATEST_DB_BLOCK}" --server "${WEBSOCKET_URL}"  \
    | db --database_url "${DATABASE_URL}" insert-blocks
}

bulk_add_checkpoint_blocks() {
  load-checkpoint-blocks --start $1 --end $2  "${CHECKPOINTS_PATH}" \
    | db --database_url "${DATABASE_URL}" bulk-add --chunksize $3 -
}

bulk_add_steemd_blocks() {
  bulk-blocks --start $1 --end $2  --url "${STEEMD_HTTP_URL}"  \
    | db --database_url "${DATABASE_URL}" bulk-add --chunksize $3  -
}


load_checkpoints() {
  # confirm required environment vars are set
  local test_var_is_test="${CHECKPOINTS_PATH:?Need to set CHECKPOINTS_PATH to local path or s3://bucket}"

  #local LATEST_DB_BLOCK="$(latest_db_block)"
  #local LATEST_BLOCKCHAIN_BLOCK="$(block-height)"
  #(>&2 echo "latest db block: ${LATEST_DB_BLOCK}")
  #(>&2 echo "latest blockchain block: ${LATEST_BLOCKCHAIN_BLOCK}")
  #bulk_add_checkpoint_blocks "${LATEST_DB_BLOCK}" "${LATEST_BLOCKCHAIN_BLOCK}" 1000

  bulk_add_checkpoint_blocks 1 1000000 300 & \
    bulk_add_checkpoint_blocks 1000001 2000000 300 & \
    bulk_add_checkpoint_blocks 2000001 3000000 300 & \
    bulk_add_checkpoint_blocks 3000001 4000000 300 & \
    bulk_add_checkpoint_blocks 4000001 5000000 300 & \
    bulk_add_checkpoint_blocks 5000001 6000000 300 & \
    bulk_add_checkpoint_blocks 6000001 7000000 300 & \
    bulk_add_checkpoint_blocks 7000001 8000000 300 & \
    bulk_add_checkpoint_blocks 8000001 0 300

}

load_steemd_blocks() {
  # confirm required environment vars are set
  local test_var_is_test="${STEEMD_HTTP_URL:?Need to set STEEMD_HTTP_URL to steemd instance}"

  #local LATEST_DB_BLOCK="$(latest_db_block)"
  #local LATEST_BLOCKCHAIN_BLOCK="$(block-height)"
  #(>&2 echo "latest db block: ${LATEST_DB_BLOCK}")
  #(>&2 echo "latest blockchain block: ${LATEST_BLOCKCHAIN_BLOCK}")
  #bulk_add_steemd_blocks "${LATEST_DB_BLOCK}" "${LATEST_BLOCKCHAIN_BLOCK}" 1000

  bulk_add_steemd_blocks 1 1000000 300 & \
    bulk_add_steemd_blocks 1000001 2000000 300 & \
    bulk_add_steemd_blocks 2000001 3000000 300 & \
    bulk_add_steemd_blocks 3000001 4000000 300 & \
    bulk_add_steemd_blocks 4000001 5000000 300 & \
    bulk_add_steemd_blocks 5000001 6000000 300 & \
    bulk_add_steemd_blocks 6000001 7000000 300 & \
    bulk_add_steemd_blocks 7000001 8000000 300 & \
    bulk_add_steemd_blocks 8000001 9000000 300 & \
    bulk_add_steemd_blocks 9000001 0 300

}


main () {
  # confirm required environment vars are set
  local test_var_is_test="${DATABASE_URL:?Need to set DATABASE_URL to db instance}"
  local test_var_is_test="${WEBSOCKET_URL:?Need to set WEBSOCKET_URL to steemd instance}"


  (>&2 echo "initializing db if required")
  db --database_url "${DATABASE_URL}" init

  # no checkpoints
  if [ -z "${CHECKPOINTS_PATH}" ]; then
    (>&2 echo "no checkpoints path specified, loading blocks from steemd")
    load_steemd_blocks
    (>&2 echo "steemd blocks loaded, streaming")
    stream_blocks
  # checkpoints
  else
    # testing checkpoints access
    test-checkpoint-access "${CHECKPOINTS_PATH}"
    if [ $? -eq 0 ]; then
      (>&2 echo "loading blocks from checkpoints")
      load_checkpoints
      (>&2 echo "checkpoints loaded, streaming")
      stream_blocks
    else
    (>&2 echo "streaming blocks")
    stream_blocks
    fi
  fi
}

main "$@"
