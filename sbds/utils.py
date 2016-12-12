# -*- coding: utf-8 -*-


# first 4 bytes (8 hex digits) of the block ID represents the block number
def blocknum_from_hash(block_hash):
    return int(str(block_hash)[:8], base=16)

def blocknum_from_previous(previous_block_hash):
    return blocknum_from_hash(previous_block_hash) + 1
