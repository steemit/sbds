# -*- coding: utf-8 -*-

import sbds.logging
logger = sbds.logging.getLogger(__name__)

# first 4 bytes (8 hex digits) of the block ID represents the block number
def block_num_from_hash(block_hash):
    return int(str(block_hash)[:8], base=16)

def block_num_from_previous(previous_block_hash):
    return block_num_from_hash(previous_block_hash) + 1
