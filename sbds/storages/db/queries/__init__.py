# -*- coding: utf-8 -*-


GET_ACCOUNT_HISTORY = '''
SELECT block_num, transaction_num, operation_num,operation_type, raw  from sbds_all_ops_view  where sbds_all_ops_view.accounts @> '["$1"]';
'''
