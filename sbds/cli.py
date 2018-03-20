# -*- coding: utf-8 -*-
import os
import logging
import sys

import click
import structlog


from sbds.chain.cli import chain
from sbds.server.cli import server
from sbds.storages.db.cli import db
from sbds.storages.s3.cli import s3
from sbds.storages.fs.cli import fs

from sbds.codegen.cli import codegen

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


logging.basicConfig(
    format="%(message)s",
    stream=sys.stderr,
    level=os.environ.get('LOG_LEVEL', 'INFO'),
)

@click.group(
    short_help='manages storage, retrieval, and querying of the Steem blockchain')
def sbds():
    """The *sbds* CLI manages storage, retrieval, and querying of the Steem
    blockchain.

    sbds has several commands, each of which has additional subcommands.

    \b
    For more detailed information on a command and its flags, run:
        sbds COMMAND --help
    """


sbds.add_command(chain)
sbds.add_command(db)
sbds.add_command(s3)
sbds.add_command(fs)
sbds.add_command(server)
sbds.add_command(codegen)

if __name__ == '__main__':
    sbds()
