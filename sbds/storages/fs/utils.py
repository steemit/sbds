# -*- coding: utf-8 -*-
import hashlib
import os.path


def key(block_num, name=None, base_path=None):
    block_num_sha = hashlib.sha1(bytes(block_num)).hexdigest()
    return os.path.join(*[part for part in (base_path,
                                            block_num_sha[:2],
                                            block_num_sha[2:4],
                                            block_num_sha[4:6],
                                            str(block_num),
                                            name) if part])
