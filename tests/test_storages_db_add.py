# -*- coding: utf-8 -*-

from sqlalchemy.orm.util import object_state

from sbds.storages.db import add_blocks
from sbds.storages.db.tables import Block


# pylint: disable=no-member
def test_add_block(blocks_with_txs, sqlitedb_session):
    results = add_blocks(blocks_with_txs, sqlitedb_session, insert=True)
    for obj, result in results:
        assert result
        state = object_state(obj)
        assert state.persistent is True

    assert Block.count(sqlitedb_session) == len(blocks_with_txs)
