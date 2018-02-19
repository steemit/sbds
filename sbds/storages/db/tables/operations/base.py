# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import SmallInteger
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from toolz.dicttoolz import dissoc

import sbds.sbds_json
import structlog

from ...query_helpers import standard_trailing_windows
from ...utils import UniqueMixin
from ..core import extract_operations_from_block
from .account_create import AccountCreateOperation
from .account_create_with_delegation import \
    AccountCreateWithDelegationOperation
from .account_update import AccountUpdateOperation
from .account_witness_proxy import AccountWitnessProxyOperation
from .account_witness_vote import AccountWitnessVoteOperation
from .cancel_transfer_from_savings import CancelTransferFromSavingsOperation
from .change_recovery_account import ChangeRecoveryAccountOperation
from .claim_reward_balance import ClaimRewardBalanceOperation
from .comment import CommentOperation
from .comment_option import CommentOptionOperation
from .convert import ConvertOperation
from .custom import CustomOperation
from .custom_json import CustomJSONOperation
from .decline_voting_rights import DeclineVotingRightsOperation
from .delegate_vesting import DelegateVestingSharesOperation
from .delete_comment import DeleteCommentOperation
from .escow_approve import EscrowApproveOperation
from .escow_transfer import EscrowTransferOperation
from .escrow_dispute import EscrowDisputeOperation
from .escrow_release import EscrowReleaseOperation
from .feed_publish import FeedPublishOperation
from .limit_oder_create import LimitOrderCreateOperation
from .limit_order_cancel import LimitOrderCancelOperation
from .pow import PowOperation
from .pow2 import Pow2Operation
from .recover_account import RecoverAccountOperation
from .request_account_recovery import RequestAccountRecoveryOperation
from .transfer import TransferOperation
from .transfer_from_savings import TransferFromSavingsOperation
from .transfer_to_savings import TransferToSavingsOperation
from .transfer_to_vesting import TransferToVestingOperation
from .vote import VoteOperation
from .withdraw_vesting import WithdrawVestingOperation
from .withdraw_vesting_route import WithdrawVestingRouteOperation
from .witness_update import WitnessUpdateOperation

logger = structlog.get_logger(__name__)


class UndefinedTransactionType(Exception):
    """Exception raised when undefined transction is encountered"""


# noinspection PyMethodParameters
class OperationMixin(UniqueMixin):
    # pylint: disable=no-self-argument

    @classmethod
    def _prepare_for_storage(cls, **kwargs):
        data_dict, _fields = dict(), dict()
        op_type = None

        try:
            data_dict = kwargs['data_dict']
            op_type = data_dict['type']
            tx_cls = cls.tx_class_for_type(op_type)
            _fields = tx_cls._fields
            prepared = {k: v(data_dict) for k, v in _fields.items()}
            prepared['block_num'] = data_dict['block_num']
            prepared['transaction_num'] = data_dict['transaction_num']
            prepared['operation_num'] = data_dict['operation_num']
            prepared['timestamp'] = data_dict['timestamp']
            prepared['operation_type'] = op_type

            if 'class_tuple' in kwargs:
                return tx_cls, prepared
            return prepared
        except Exception as e:
            extra = dict(
                block_num=data_dict.get('block_num'),
                transaction_num=data_dict.get('transaction_num'),
                operation_num=data_dict.get('operation_num'),
                timestamp=data_dict.get('timestamp'),
                op_type=op_type,
                _fields=_fields,
                error=e,
                **kwargs)
            logger.error(e, extra=extra)
            return None

    @classmethod
    def from_raw_block(cls, raw_block):
        operations = list(extract_operations_from_block(raw_block))
        if not operations:
            # root_logger.debug('no transactions extracted from block')
            return []

        bn = operations[0].get('block_num', '')
        logger.debug('extracted %s operations from block %s',
                     len(operations), bn)
        prepared = [cls._prepare_for_storage(data_dict=d) for d in operations]
        objs = []
        for i, prepared_tx in enumerate(prepared):
            op_type = operations[i]['type']
            try:
                tx_cls = cls.tx_class_for_type(op_type)
            except UndefinedTransactionType as e:
                logger.error(e)
                continue
            else:
                logger.debug('operation type %s mapped to class %s', op_type,
                             tx_cls.__name__)
                objs.append(tx_cls(**prepared_tx))
                logger.debug('instantiated: %s',
                             [o.__class__.__name__ for o in objs])
        return objs

    @classmethod
    def tx_class_for_type(cls, tx_type):
        try:
            return op_class_map[tx_type]
        except KeyError:
            raise UndefinedTransactionType(tx_type)

    # pylint: disable=unused-argument
    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return tuple([
            kwargs['block_num'], kwargs['transaction_num'],
            kwargs['operation_num']
        ])

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        return query.filter(
            cls.block_num == kwargs['block_num'],
            cls.transaction_num == kwargs['transaction_num'],
            cls.operation_num == kwargs['operation_num'], )

    # pylint: enable=unused-argument

    @classmethod
    def from_to_filter(cls, query, _from=None, to=None):
        if isinstance(_from, int):
            query = cls.block_num_window_filter(query, _from=_from)
        elif isinstance(_from, datetime):
            query = cls.datetime_window_filter(query, _from=_from)

        if isinstance(to, int):
            query = cls.block_num_window_filter(query, to=to)
        elif isinstance(to, datetime):
            query = cls.datetime_window_filter(query, to=to)

        return query

    @classmethod
    def block_num_window_filter(cls, query, _from=None, to=None):
        if _from:
            query = query.filter(cls.block_num >= _from)
        if to:
            query = query.filter(cls.block_num <= to)
        return query

    @classmethod
    def datetime_window_filter(cls, query, _from=None, to=None):
        if _from:
            query = query.filter(cls.timestamp >= _from)
        if to:
            query = query.filter(cls.timestamp <= to)
        return query

    @classmethod
    def standard_trailing_windowed_queries(cls, query):
        """

        Args:
            query (sqlalchemy.orm.query.Query):

        Yields:
            sqlalchemy.orm.query.Query
        """
        for window in standard_trailing_windows():
            yield cls.datetime_window_filter(query, **window)

    @classmethod
    def standard_windowed_count(cls, session):
        count_query = cls.count_query(session)
        for window_query in cls.standard_trailing_windowed_queries(
                count_query):
            yield window_query.scalar()

    @classmethod
    def _count_index_name(cls):
        # pylint: disable=no-member
        return 'ix_%s_timestamp' % cls.__tablename__

    @classmethod
    def count_query(cls, session):
        ix = cls._count_index_name()
        ix_stmt = 'USE INDEX(%s)' % ix
        return session.query(func.count(cls.timestamp)).with_hint(cls, ix_stmt)

    def dump(self):
        return dissoc(self.__dict__, '_sa_instance_state')

    def to_dict(self, decode_json=True):
        data_dict = self.dump()
        if isinstance(data_dict.get('json_metadata'), str) and decode_json:
            data_dict['json_metadata'] = sbds.sbds_json.loads(
                data_dict['json_metadata'])
        return data_dict

    def to_json(self):
        data_dict = self.to_dict()
        return sbds.sbds_json.dumps(data_dict)

    def __repr__(self):
        return "<%s (block_num:%s transaction_num: %s operation_num: %s keys: %s)>" % (
            self.__class__.__name__, self.block_num, self.transaction_num,
            self.operation_num, tuple(self.dump().keys()))

    def __str__(self):
        return str(self.dump())

# noinspection PyMethodParameters
class BaseOperation(OperationMixin):
    # pylint: disable=no-self-argument

    @declared_attr
    def __table_args__(cls):
        args = (PrimaryKeyConstraint('block_num', 'transaction_num',
                                     'operation_num'), {
                                         'mysql_engine': 'InnoDB',
                                         'mysql_charset': 'utf8mb4',
                                         'mysql_collate': 'utf8mb4_general_ci'
        })
        return getattr(cls, '__extra_table_args__', tuple()) + args

    # pylint: enable=no-self-argument

    block_num = Column(Integer, nullable=False, index=True)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False), index=True)

    _fields = dict()




class BaseVirtualOperation(OperationMixin):
    # pylint: disable=no-self-argument

    __table_args__ = ({
                          'mysql_engine':  'InnoDB',
                          'mysql_charset': 'utf8mb4',
                          'mysql_collate': 'utf8mb4_general_ci'
                      },)

    # pylint: enable=no-self-argument

    block_num = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=False), nullable=False, index=True)

    _fields = dict()




# pylint: disable=line-too-long, bad-continuation, too-many-lines, no-self-argument

# These are defined in the steem source code here:
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/operations.hpp
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/steem_operations.hpp
op_class_map = {
    'account_create': AccountCreateOperation,
    'account_create_with_delegation': AccountCreateWithDelegationOperation,
    'account_update': AccountUpdateOperation,
    'account_witness_proxy': AccountWitnessProxyOperation,
    'account_witness_vote': AccountWitnessVoteOperation,
    'cancel_transfer_from_savings': CancelTransferFromSavingsOperation,
    'change_recovery_account': ChangeRecoveryAccountOperation,
    'claim_reward_balance': ClaimRewardBalanceOperation,
    'comment': CommentOperation,
    'comment_options': CommentOptionOperation,
    'convert': ConvertOperation,
    'custom': CustomOperation,
    'custom_json': CustomJSONOperation,
    'decline_voting_rights': DeclineVotingRightsOperation,
    'delegate_vesting_shares': DelegateVestingSharesOperation,
    'delete_comment': DeleteCommentOperation,
    'escrow_approve': EscrowApproveOperation,
    'escrow_dispute': EscrowDisputeOperation,
    'escrow_release': EscrowReleaseOperation,
    'escrow_transfer': EscrowTransferOperation,
    'feed_publish': FeedPublishOperation,
    'limit_order_cancel': LimitOrderCancelOperation,
    'limit_order_create': LimitOrderCreateOperation,
    'pow': PowOperation,
    'pow2': Pow2Operation,
    'recover_account': RecoverAccountOperation,
    'request_account_recovery': RequestAccountRecoveryOperation,
    'set_withdraw_vesting_route': WithdrawVestingRouteOperation,
    'transfer': TransferOperation,
    'transfer_from_savings': TransferFromSavingsOperation,
    'transfer_to_savings': TransferToSavingsOperation,
    'transfer_to_vesting': TransferToVestingOperation,
    'vote': VoteOperation,
    'withdraw_vesting': WithdrawVestingOperation,
    'witness_update': WitnessUpdateOperation
}


# virtual operations
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/steem_virtual_operations.hpp
virtual_op_class_map = {
    'author_reward_operation':None,
    'curation_reward_operation': None,
    'comment_reward_operation': None,
    'liquidity_reward_operation':None,
    'interest_operation':None,
    'fill_convert_request_operation':None,
    'fill_vesting_withdraw_operation': None,
    'shutdown_witness_operation': None,
    'fill_order_operation': None,
    'fill_transfer_from_savings_operation': None,
    'hardfork_operation': None,
    'comment_payout_update_operation': None,
    'return_vesting_delegation_operation': None,
    'comment_benefactor_reward_operation': None,
    'producer_reward_operation': None
}

combined_ops_class_map = dict(**op_class_map, **virtual_op_class_map)
