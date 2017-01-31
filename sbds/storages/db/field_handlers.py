# -*- coding: utf-8 -*-
import json

import sbds.logging
from sbds.utils import build_comment_url

logger = sbds.logging.getLogger(__name__)


def example_field_handler(value=None, context=None, **kwargs):
    """
    :param value: value received from field lambda function
    :param context: all values of the dict populating the instance
    :param kwargs: any additional params required
    :return: value, modified or not
    """


def author_field(context=None, author_name=None, session=None):
    return author_name


# noinspection PyArgumentList
def images_field(context=None, meta=None, body=None, session=None):
    from sbds.storages.db.tables.synthesized import Image
    meta_json = json_metadata_field(meta)
    urls = meta_json.get('images', [])
    images = []
    for url in urls:
        images.append(Image(url=url,
                            extraction_source='meta'))  # TODO Do these need to be unique to post?
    return images


# noinspection PyArgumentList
def links_field(context=None, meta=None, body=None, session=None):
    from sbds.storages.db.tables.synthesized import Link
    meta_json = json_metadata_field(meta)
    urls = meta_json.get('links', [])
    links = []
    for url in urls:
        links.append(Link(url=url,
                          extraction_source='meta'))  # TODO Do these need to be unique to post?
    return links


def tags_field(context=None, meta=None, body=None, session=None):
    from sbds.storages.db.tables.synthesized import Tag
    meta_json = json_metadata_field(meta)
    found_tags = meta_json.get('tags', [])
    tags = []
    for tag in found_tags:
        tags.append(Tag.as_unique(session, id=tag))
    return tags


def json_metadata_field(value):
    if not value:
        return None
    metadata = metadata2 = None
    try:
        metadata = json.loads(value)
        if isinstance(metadata, dict):
            return metadata
        elif isinstance(metadata, str):
            if metadata == "":
                return None
            else:
                metadata2 = json.loads(metadata)
                return metadata
    except Exception as e:
        extra = dict(original=value, metadata=metadata, metadata2=metadata2,
                     error=e)
        logger.error('json_metadata handler error', extra=extra)
        return None


def amount_field(value, num_func=int, no_value=0):
    if not value:
        return num_func(no_value)
    try:
        return num_func(value.split()[0])
    except Exception as e:
        extra = dict(original=value, num_func=num_func, no_value=no_value,
                     error=e)
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


def url_field(value=None, context=None, **kwargs):
    """

    :param value:
    :param context:
    :param kwargs:
    :return:
    """
    return build_comment_url(context.get('parent_permlink'),
                             context.get('author'), context.get('permlink'))


def comment_parent_id_field(context=None, session=None):
    from sbds.storages.db.tables.tx import TxComment
    if context['type'] == 'post':
        logger.debug('Posts have no parents, returning None')
        return None
    block_num = context.get('block_num')
    transaction_num = context.get('transaction_num')
    operation_num = context.get('operation_num')
    txcomment = session.query(TxComment).filter_by(block_num=block_num,
                                                   transaction_num=transaction_num,
                                                   operation_num=operation_num
                                                   ).one_or_none()

    logger.debug('query for TxComment yielded %s', txcomment)
    if not txcomment:
        logger.debug('no txcomment, returning None')
        return None
    q = session.query(TxComment).filter_by(
            parent_author=txcomment.parent_author,
            parent_permlink=txcomment.parent_permlink)
    q.order_by(TxComment.block_num, TxComment.transaction_num,
               TxComment.operation_num)
    txcomment_parent = q.first()
    if txcomment_parent:
        if context['type'] == 'post':
            from sbds.storages.db.tables.synthesized import Post
            cls = Post
        else:
            from sbds.storages.db.tables.synthesized import Comment
            cls = Comment
        logger.debug('txcomment class is %s', cls.__name__)
        parent_post_comment = session.query(cls).filter_by(
                block_num=txcomment_parent.block_num,
                transaction_num=txcomment_parent.transaction_num,
                operation_num=txcomment_parent.operation_num
        ).one_or_none()

        logger.debug('parent %s query returned %s', cls.__name__,
                     parent_post_comment)
        if parent_post_comment:
            return parent_post_comment.id
        else:
            logger.debug('no %s parent, returning None', cls.__name__)
            return None
    else:
        logger.debug('no txcomment_parent, returning None')
        return None
