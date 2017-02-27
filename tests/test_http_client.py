# -*- coding: utf-8 -*-


def test_client_get_block(http_client, first_block_dict):
    block = http_client.get_block(1)
    assert block == first_block_dict
