# -*- coding: utf-8 -*-

import sbds.logging
from sbds.utils import build_comment_url
from sbds.utils import canonicalize_url
from sbds.utils import detect_language
from sbds.utils import ensure_decoded
from sbds.utils import extract_keys_from_meta
from sbds.utils import findall_patch_hunks

logger = sbds.logging.getLogger(__name__)


def example_field_handler(value=None, context=None, **kwargs):
    """

    Args:
      value: value received from field lambda function (Default value = None)
      context: all values of the dict populating the instance (Default value = None)
      kwargs: any additional params required
      **kwargs: 

    Returns:
      value, modified or not

    """


def author_field(context=None, author_name=None, session=None):
    from .tables import Account
    account = Account.as_unique(
        session, name=author_name, created=context.get('timestamp'))
    return account.name


# noinspection PyArgumentList
def images_field(meta=None):
    from sbds.storages.db.tables.synthesized import Image
    default = []
    decoded = ensure_decoded(meta)
    if not decoded:
        return default
    found_urls = extract_keys_from_meta(decoded, ('image', 'images'))
    images = []
    for url in found_urls:
        canon_url = canonicalize_url(url)
        if not url:
            logger.warning('skipping bad url: %s', url)
            continue
        images.append(Image(url=canon_url, extraction_source='meta')
                      )  # TODO Do these need to be unique to post?
    return images


# noinspection PyArgumentList
def links_field(meta=None):
    from sbds.storages.db.tables.synthesized import Link
    default = []
    decoded = ensure_decoded(meta)
    if not decoded:
        return default
    found_urls = extract_keys_from_meta(decoded, ('link', 'links'))
    links = []
    for url in found_urls:
        canon_url = canonicalize_url(url)
        if not url:
            logger.warning('skipping bad url: %s', url)
            continue
        links.append(Link(url=canon_url, extraction_source='meta')
                     )  # TODO Do these need to be unique to post?
    return links


def tags_field(meta=None, session=None):
    from sbds.storages.db.tables.synthesized import Tag
    default = []
    decoded = ensure_decoded(meta)
    if not decoded:
        return default
    found_tags = extract_keys_from_meta(decoded, ('tag', 'tags'))
    tags = []
    for tag in found_tags:
        tags.append(Tag.as_unique(session, id=tag))
    return tags


def amount_field(value, num_func=int, no_value=0):
    if not value:
        return num_func(no_value)
    try:
        return num_func(value.split()[0])
    except Exception as e:
        extra = dict(
            original=value, num_func=num_func, no_value=no_value, error=e)
        logger.error('amount handler error', extra=extra)
        return num_func(no_value)


def amount_symbol_field(value, no_value=''):
    if not value:
        return no_value
    try:
        return value.split()[1]
    except Exception as e:
        extra = dict(original=value, no_value=no_value, error=e)
        logger.error('amount_symbol handler error', extra=extra)
        return no_value


def comment_body_field(value):
    if isinstance(value, bytes):
        return value.decode('utf8')
    else:
        return value


def url_field(context=None):
    """

    Args:
      context: return: (Default value = None)

    Returns:

    """
    return build_comment_url(
        context.get('parent_permlink'),
        context.get('author'), context.get('permlink'))


def comment_parent_id_field(context=None, session=None):
    from sbds.storages.db.tables.tx import TxComment
    block_num = context.get('block_num')
    transaction_num = context.get('transaction_num')
    operation_num = context.get('operation_num')

    # Step 1) exclude all posts (posts have not parents)
    if context['type'] == 'post':
        logger.debug('Posts have no parents, returning None')
        return None

    # Step 2) select TxComment source of this comment
    txcomment = context.get('txcomment')
    if not txcomment:
        logger.debug('tcomment not found in context, querying')
        txcomment = session.query(TxComment).filter_by(
            block_num=block_num,
            transaction_num=transaction_num,
            operation_num=operation_num).one_or_none()
        logger.debug('query for TxComment yielded %s', txcomment)
        if not txcomment:
            # this shouldnt happen
            logger.error(
                'no txcomment found, returning None: block_num:%s transaction_num:%s operation_num:%s',
                block_num, transaction_num, operation_num)
            return None
    else:
        logger.debug('txcomment retreived from context')

    # Step 3) find this txcomment's parents, return if None
    q = session.query(TxComment).filter_by(
        author=txcomment.parent_author, permlink=txcomment.parent_permlink)
    q = q.filter(TxComment.block_num <= txcomment.block_num)
    q.order_by(-TxComment.timestamp)
    txcomment_parents = q.all()
    logger.debug('located %s parents of txcomment: %s',
                 len(txcomment_parents), txcomment_parents)
    if not txcomment_parents:
        return None
    else:
        txcomment_parent = txcomment_parents[0]

    if not txcomment_parent:
        # this should not happen
        logger.error(
            'no txcomment_parent, returning None: block_num:%s transaction_num:%s operation_num:%s',
            block_num, transaction_num, operation_num)
        return None

    # Step 4) find parent Comment from parent txcomment
    from sbds.storages.db.tables.synthesized import PostAndComment
    parent_post_and_comment = session.query(PostAndComment).filter_by(
        block_num=txcomment_parent.block_num,
        transaction_num=txcomment_parent.transaction_num,
        operation_num=txcomment_parent.operation_num).first()

    logger.debug('parent PostAndComment query returned %s',
                 parent_post_and_comment)
    if parent_post_and_comment:
        logger.debug(
            'parent PostAndComment found, returning parent Comment.id: %s',
            parent_post_and_comment.id)
        return parent_post_and_comment.id
    else:
        logger.debug('no PostAndComment parent, returning None')
        return None


def has_patch_field(body=None):
    if findall_patch_hunks(body):
        return True
    return False


def language_field(body=None):
    return detect_language(body)
