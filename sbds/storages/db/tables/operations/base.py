# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import SmallInteger
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from toolz.dicttoolz import dissoc

import sbds.sbds_json
import structlog

from ...query_helpers import standard_trailing_windows
from ...utils import UniqueMixin
from ..core import extract_operations_from_block


logger = structlog.get_logger(__name__)


class UndefinedTransactionType(Exception):
    """Exception raised when undefined transction is encountered"""
