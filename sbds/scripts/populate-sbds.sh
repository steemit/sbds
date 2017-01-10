#!/usr/bin/env bash

BLOCK_HEIGHT=$(block-height)


sbds | pv --line-mode --size ${BLOCK_HEIGHT} --name Blocks | tee \
    >(db --database_url "${DATABASE_URL}" insert-blocks) \
    >(db --database_url "${DATABASE_URL}" insert-transactions) \
    > /dev/null