#!/usr/bin/env bash

sbds | pv  --progress --rate --eta --timer --average-rate --line-mode --size $(block-height) --name Blocks | tee \
    >(db --database_url "${DATABASE_URL}" insert-blocks) \
    >(db --database_url "${DATABASE_URL}" insert-transactions) \
    > /dev/null
