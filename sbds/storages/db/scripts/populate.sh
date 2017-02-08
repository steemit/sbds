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


stream_blocks() {
  sbds --start ${LATEST_DB_BLOCK} --server "${WEBSOCKET_URL}"  \
    | db --database_url "${DATABASE_URL}" insert-blocks
}

insert_checkpoint_blocks() {
  load-checkpoint-blocks --start $1 --end $2 "${CHECKPOINTS_PATH}" \
    | db --database_url "${DATABASE_URL}" bulk-add -
}

main () {
  # confirm required environment vars are set
  local test_var_is_test="${DATABASE_URL:?Need to set DATABASE_URL non-empty}"
  local test_var_is_test="${CHECKPOINTS_PATH:?Need to set CHECKPOINTS_PATH to local path or s3://bucket}"
  insert_checkpoint_blocks 1 1000000 & \
 insert_checkpoint_blocks 1000001 2000000 & \
 insert_checkpoint_blocks 2000001 3000000 & \
 insert_checkpoint_blocks 3000001 4000000 & \
 insert_checkpoint_blocks 4000001 5000000 & \
 insert_checkpoint_blocks 5000001 6000000 & \
 insert_checkpoint_blocks 6000001 7000000 & \
 insert_checkpoint_blocks 7000001 8000000 & \
 insert_checkpoint_blocks 8000001 0

  stream_blocks


}

main "$@"
