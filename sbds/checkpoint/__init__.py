# -*- coding: utf-8 -*-
import fileinput
import fnmatch
import json
import os
import re

import toolz.itertoolz

import sbds.logging

logger = sbds.logging.getLogger(__name__)

CHECKPOINT_FILENAME_PATTERN =  'blocks_*.json*'
COMPRESSED_CHECKPOINT_FILENAME_PATTERN = 'blocks_*.json.gz'

CHECKPOINT_FILENAME_REGEX_PATTERN = r'blocks_(?P<start>[0-9]+)-(?P<end>[0-9]+)\.json(?P<is_gzipped>\.gz$)?'
CHECKPOINT_FILENAME_REGEX = re.compile(CHECKPOINT_FILENAME_REGEX_PATTERN)

MIN_LEFTPAD_AMOUNT = 6


def load_blocks_from_checkpoints(checkpoints_dir, start, end):
    """Load blocks from locally stored "checkpoint" files"""

    checkpoint_filenames = required_checkpoint_files(path=checkpoints_dir, start=start, end=end)

    checkpoint_filenames = sorted(checkpoint_filenames)
    first_checkpoint_file_offset = calculate_offset(start, checkpoint_filenames[0])
    with fileinput.FileInput(mode='r',
                             files=checkpoint_filenames,
                             openhook=hook_compressed_encoded('utf8')) as blocks:
        offset_blocks = toolz.itertoolz.drop(first_checkpoint_file_offset, blocks)
        for block in offset_blocks:
            yield block


def required_checkpoint_files(path, start, end=None, files=None):
    checkpoint_file_pattern = 'blocks_*.json*'
    all_files = os.listdir(path)
    files = files or fnmatch.filter(all_files, checkpoint_file_pattern)
    checkpoint_files = []
    for file in files:
        check_low = int(file.split('-')[0].split('_')[1])
        check_high = int(file.split('-')[1].split('.')[0])
        if start > check_high:
            continue
        if end and end > 0 and check_low > end:
            break
        checkpoint_files.append(file)

    return [os.path.join(path, f) for f in checkpoint_files]


def roundup(x, factor=1000000):
    return x if x % factor == 0 else x + factor - x % factor


def rounddown(x, factor=1000000):
    return (x // factor) * factor


def calculate_offset(starting_block_num, first_required_checkpoint_filename):
    file_starting_blocknum, end_starting_blocknum = start_and_end_from_checkpoint_filename(first_required_checkpoint_filename)
    return starting_block_num - file_starting_blocknum

def start_and_end_from_checkpoint_filename(checkpoint_filename):
    start, end, is_gzipped = parse_checkpoint_filename(checkpoint_filename)
    return int(start), int(end)

def parse_checkpoint_filename(filename):
    matches = CHECKPOINT_FILENAME_REGEX.match(filename)
    start, end, is_gzipped = matches.groups()
    if is_gzipped is None:
        is_gzipped = False
    return start, end, is_gzipped

def block_num_to_str(block_num, left_pad_amount=MIN_LEFTPAD_AMOUNT):
    s = str(block_num)
    while len(s) < left_pad_amount + 1:
        s = '0' + s
    return s

def hook_compressed_encoded(encoding, real_mode='rt'):
    def openhook_compressed(filename, mode):
        ext = os.path.splitext(filename)[1]
        if ext == '.gz':
            import gzip
            return gzip.open(filename, mode=real_mode, encoding=encoding)
        elif ext == '.bz2':
            import bz2
            return bz2.BZ2File(filename, mode=real_mode, encoding=encoding)
        else:
            return open(filename, mode=real_mode, encoding=encoding)

    return openhook_compressed