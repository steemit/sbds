# -*- coding: utf-8 -*-
import fnmatch
import os
import re
from collections import namedtuple

import sbds.logging

logger = sbds.logging.getLogger(__name__)

# shell/glob patterns
CHECKPOINT_FILENAME_PATTERN = 'blocks_*-*.json*'
COMPRESSED_CHECKPOINT_FILENAME_PATTERN = 'blocks_*-*.json.gz'
S3_KEY_PATTERN = '*/%s' % CHECKPOINT_FILENAME_PATTERN

# regex patterns
CHECKPOINT_FILENAME_REGEX_PATTERN = r'blocks_(?P<start>[0-9]+)-(?P<end>[0-9]+)\.json(?P<is_gzipped>\.gz$)?'
CHECKPOINT_FILENAME_REGEX = re.compile(CHECKPOINT_FILENAME_REGEX_PATTERN)

# format string
CHECKPOINT_FILENAME_FORMAT_STRING = 'blocks-{start}-{end}.json{gzip}'

BLOCKS_PER_CHECKPOINT = 1000000
MIN_LEFTPAD_AMOUNT = str(BLOCKS_PER_CHECKPOINT).count('0')

CheckpointFile = namedtuple('CheckpointFile',
                            ['path',
                             'filename',
                             'dirname',
                             'start',
                             'end',
                             'total',
                             'is_gzipped',
                             'is_local',
                             'is_s3',
                             'filename_shell_pattern',
                             'filename_regex_pattern',
                             'blocks_per_checkpoint',
                             'available_block_space',
                             'min_left_pad'
                             ]
                            )

CheckpointSet = namedtuple('CheckpointSet',
                           ['checkpoints',
                            'checkpoint_paths',
                            'start',
                            'end',
                            'total',
                            'checkpoint_count',
                            'dirname',
                            'missing',
                            'is_consequtive',
                            'initial_checkpoint_offset',
                            'is_local',
                            'is_s3',
                            ]
                           )


# main module functions
def required_checkpoints_for_range(path, start, end=None):
    checkpointset = checkpointset_from_path(path)
    checkpoints = []
    for cp in checkpointset.checkpoints:
        check_low = cp.start
        check_high = cp.end
        if start > check_high:
            continue
        if end and 0 < end < check_low:
            break
        checkpoints.append(cp)
    offset = calculate_initial_checkpoint_offset(start, checkpoints[0])
    required_checkpointset = checkpointset_from_checkpoints(checkpoints,
                                                            initial_checkpoint_offset=offset)
    return required_checkpointset


def update_checkpoints(path, blockchain_height, rpc):
    checkpoint_set = checkpointset_from_path(path)
    if checkpoint_set.checkpoints[0].is_gzipped:
        raise TypeError('Cannot update gzipped checkpoint set directly')
    if not checkpoint_set.is_consequtive:
        raise ValueError('Cannot update non-consequtive checkpoint set')
    if checkpoint_set.end >= blockchain_height:
        logger.debug('No blocks missing')
        return

    num_cps_required = number_of_checkpoints_required(blockchain_height)
    logger.debug('%s new checkpoints required')

    num_cps_missing = num_cps_required - checkpoint_set.checkpoint_count
    logger.debug('%s new checkpoints missing')

    if num_cps_missing == 0 and checkpoint_set.end < blockchain_height:
        logger.debug('extending existing checkpoint')

        # TODO
        # num_cps_missing == 0
        # 1) extend/fill exiting cp

        # num_cps_missing > 0
        # 1) fill exiting cp
        # 2) create new cps


# checkpoint functions

default_checkpoint_file = CheckpointFile(
        path='',
        filename='',
        dirname='',
        start='',
        end='',
        total='',
        is_gzipped='',
        is_local='',
        is_s3='',
        filename_shell_pattern=CHECKPOINT_FILENAME_PATTERN,
        filename_regex_pattern=CHECKPOINT_FILENAME_REGEX_PATTERN,
        blocks_per_checkpoint=BLOCKS_PER_CHECKPOINT,
        available_block_space='',
        min_left_pad=MIN_LEFTPAD_AMOUNT)


def get_checkpoints_from_path(path):
    if path.startswith('s3://'):
        return get_checkpoints_from_s3_path(path)
    else:
        return get_checkpoints_from_local_path(path)


def get_checkpoints_from_local_path(path):
    all_files = os.listdir(path)
    files = fnmatch.filter(all_files, CHECKPOINT_FILENAME_PATTERN)
    checkpoints = []
    for f in files:
        try:
            file_path = os.path.join(path, f)
            checkpoints.append(parse_checkpoint_filename(file_path))
        except ValueError:
            continue
    return sorted(checkpoints, key=lambda cp: cp.start)


def get_checkpoints_from_s3_path(path):
    import boto3
    s3_resource = boto3.resource('s3')
    bucket_name, key_name = split_s3_bucket_key(path)
    bucket = s3_resource.Bucket(bucket_name)
    all_objects = list(bucket.objects.filter(Prefix=key_name))
    all_keys = [o.key for o in all_objects]
    keys = fnmatch.filter(all_keys, S3_KEY_PATTERN)
    checkpoints = []
    for f in keys:
        try:
            file_path = os.path.join(bucket_name, f)
            checkpoints.append(parse_checkpoint_s3_path(file_path))
        except ValueError:
            continue
    return sorted(checkpoints, key=lambda cp: cp.start)


def count_checkpoints(path):
    return len(get_checkpoints_from_path(path))


# checkpoint set functions
def checkpointset_from_path(path):
    return checkpointset_from_checkpoints(get_checkpoints_from_path(path))


def is_consequtive(checkpoints):
    missing = []
    for i, cp in enumerate(checkpoints):
        if i == 0:
            if cp.start != 1:
                missing.append(0)
            continue
        if cp.start != (checkpoints[i - 1].end + 1):
            missing.append(
                    checkpoint_filename_from_zero_index(i, cp.is_gzipped))
    return len(missing) == 0, missing


def checkpointset_from_checkpoints(checkpoints, initial_checkpoint_offset=None):
    initial_checkpoint_offset = initial_checkpoint_offset or 0
    start = checkpoints[0].start
    end = checkpoints[-1].end
    total = sum(cp.total for cp in checkpoints)
    checkpoint_paths = [cp.path for cp in checkpoints]
    dirname = checkpoints[0].dirname
    consequtive, missing = is_consequtive(checkpoints)
    is_local = checkpoints[0].is_local
    is_s3 = checkpoints[0].is_s3
    return CheckpointSet(
            checkpoints=checkpoints,
            checkpoint_paths=checkpoint_paths,
            start=start,
            end=end,
            total=total,
            checkpoint_count=len(checkpoints),
            dirname=dirname,
            missing=missing,
            is_consequtive=consequtive,
            initial_checkpoint_offset=initial_checkpoint_offset,
            is_local=is_local,
            is_s3=is_s3
    )


# checkpoints math functions

def roundup(x, factor=BLOCKS_PER_CHECKPOINT):
    return x if x % factor == 0 else x + factor - x % factor


def rounddown(x, factor=BLOCKS_PER_CHECKPOINT):
    return (x // factor) * factor


def number_of_checkpoints_required(end):
    return int(roundup(end) / BLOCKS_PER_CHECKPOINT)


def generate_checkpoint_intervals(end):
    num_required = number_of_checkpoints_required(end)
    intervals = []
    for i in range(1, num_required + 1):
        _start = ((i - 1) * BLOCKS_PER_CHECKPOINT) + 1
        _end = (i * BLOCKS_PER_CHECKPOINT)
        if _end > end:
            _end = end
        intervals.append(tuple([_start, _end]))
    return intervals


def calculate_initial_checkpoint_offset(starting_block_num, initial_checkpoint):
    return starting_block_num - initial_checkpoint.start


def start_and_end_from_checkpoint_filename(checkpoint_filename):
    cp = parse_checkpoint_filename(checkpoint_filename)
    return cp.start, cp.end


def calculate_available_block_space(start, end, size=BLOCKS_PER_CHECKPOINT):
    return size - ((end + 1) - start)


# checkpoints string functions
def parse_checkpoint_filename(filename_or_path):
    filename = os.path.basename(filename_or_path)
    matches = CHECKPOINT_FILENAME_REGEX.match(filename)
    start, end, is_gzipped = matches.groups()
    if is_gzipped is None:
        is_gzipped = False
    else:
        is_gzipped = True

    start = int(start)
    end = int(end)
    total = (end + 1) - start
    cp = default_checkpoint_file._replace(
            start=start,
            end=end,
            total=total,
            path=os.path.abspath(filename_or_path),
            filename=filename,
            dirname=os.path.dirname(os.path.abspath(filename_or_path)),
            is_gzipped=is_gzipped,
            is_local=True,
            is_s3=False,
            available_block_space=calculate_available_block_space(start, end)
    )
    if not any([cp.start, cp.end, cp.path, cp.total, cp.available_block_space]):
        raise ValueError('Bad values for CheckpointFile: %s' % cp)
    return cp


def parse_checkpoint_s3_path(path):
    bucket, key = split_s3_bucket_key(path)
    filename = os.path.basename(key)
    matches = CHECKPOINT_FILENAME_REGEX.match(filename)
    start, end, is_gzipped = matches.groups()
    if is_gzipped is None:
        is_gzipped = False
    else:
        is_gzipped = True

    path = 's3://%s' % os.path.join(bucket, key)
    start = int(start)
    end = int(end)
    total = (end + 1) - start
    cp = default_checkpoint_file._replace(
            start=start,
            end=end,
            total=total,
            path=path,
            filename=filename,
            dirname=os.path.dirname(key),
            is_gzipped=is_gzipped,
            is_local=False,
            is_s3=True,
            available_block_space=calculate_available_block_space(start, end)
    )
    if not any([cp.start, cp.end, cp.path, cp.total, cp.available_block_space]):
        raise ValueError('Bad values for CheckpointFile: %s' % cp)
    return cp


def block_num_to_str(block_num, left_pad_amount=MIN_LEFTPAD_AMOUNT):
    s = str(block_num)
    while len(s) < left_pad_amount + 1:
        s = '0' + s
    return s


def checkpoint_filename_from_zero_index(index, is_gzipped=True):
    start = block_num_to_str((index * BLOCKS_PER_CHECKPOINT) + 1)
    end = block_num_to_str(((index + 1) * BLOCKS_PER_CHECKPOINT))
    if is_gzipped:
        gzip = '.gz'
    else:
        gzip = ''
    return CHECKPOINT_FILENAME_FORMAT_STRING.format(start=start, end=end,
                                                    gzip=gzip)


# checkpoint file/data functions
def add_blocks_to_existing_checkpoint(cp, blocks):
    # TODO
    pass


def add_blocks_to_new_checkpoint(path, blocks):
    # TODO
    pass


def checkpoint_opener_wrapper(encoding='utf8', real_mode='rt'):
    def checkpoint_opener(filename, mode):
        ext = os.path.splitext(filename)[1]
        logger.debug('checkpoint ext: %s', ext)
        # checkpoint stored in s3
        if filename.startswith('s3://'):
            logger.debug('loading s3 checkpoint: %s', filename)
            import boto3
            import io
            s3_resource = boto3.resource('s3')
            bucket, key = split_s3_bucket_key(filename)
            logger.debug('s3 obj bucket:%s key:%s', bucket, key)
            obj = s3_resource.Object(bucket, key)
            data = obj.get()

            if ext == '.gz':
                logger.debug('opening s3 gzipped checkpoint: %s', filename)
                import gzip
                buffer = gzip.GzipFile(fileobj=data['Body'])

            else:
                logger.debug('opening s3 checkpoint: %s', filename)
                buffer = data['Body']
            return io.TextIOWrapper(buffer=buffer,
                                    encoding=encoding)
        else:
            # local checkpoint
            logger.debug('loading local checkpoint')
            if ext == '.gz':
                logger.debug('opening local gzipped checkpoint: %s', filename)
                import gzip
                return gzip.open(filename, mode=real_mode, encoding=encoding)

            else:
                logger.debug('opening local checkpoint: %s', filename)
                return open(filename, mode=real_mode, encoding=encoding)

    return checkpoint_opener


# parsing functions taken from awscli library
# https://github.com/aws/aws-cli/blob/develop/awscli/customizations/s3/utils.py#L179
def find_bucket_key(s3_path):
    """
    This is a helper function that given an s3 path such that the path is of
    the form: bucket/key
    It will return the bucket and the key represented by the s3 path
    """
    s3_components = s3_path.split('/')
    bucket = s3_components[0]
    s3_key = ""
    if len(s3_components) > 1:
        s3_key = '/'.join(s3_components[1:])
    return bucket, s3_key


def split_s3_bucket_key(s3_path):
    """Split s3 path into bucket and key prefix.
    This will also handle the s3:// prefix.
    :return: Tuple of ('bucketname', 'keyname')
    """
    if s3_path.startswith('s3://'):
        s3_path = s3_path[5:]
    return find_bucket_key(s3_path)
