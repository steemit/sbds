# -*- coding: utf-8 -*-
import os
import logging
import sys

import click
import structlog

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

cmd_map = {
    'chain': 'sbds/chain/cli.py',
    'server': 'sbds/server/cli.py',
    'db': 'sbds/storages/db/cli.py',
    'fs': 'sbds/storages/fs/cli.py',
    's3': 'sbds/storages/s3/cli.py',
    'codegen': 'sbds/codegen/cli.py'
}


class MyCLI(click.MultiCommand):

    def list_commands(self, ctx):
        return ['chain', 'server', 'db', 's3', 'fs', 'codegen']

    def get_command(self, ctx, name):
        ns = {}
        fn = cmd_map[name]
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, globals())
        return ns['cli']


@click.group(
    short_help='manages storage, retrieval, and querying of the Steem blockchain')
def sbds_cli():
    """The *sbds* CLI manages storage, retrieval, and querying of the Steem
    blockchain.

    sbds has several commands, each of which has additional subcommands.

    \b
    For more detailed information on a command and its flags, run:
        sbds COMMAND --help
    """


if __name__ == '__main__':
    import sbds.chain.cli
    import sbds.server.cli
    import sbds.storages.db.cli
    import sbds.storages.s3.cli
    import sbds.storages.fs.cli
    import sbds.codegen.cli
    sbds_cli.add_command(sbds.chain.cli.cli)
    sbds_cli.add_command(sbds.server.cli.cli)
    sbds_cli.add_command(sbds.storages.db.cli.cli)
    sbds_cli.add_command(sbds.storages.s3.cli.cli)
    sbds_cli.add_command(sbds.storages.fs.cli.cli)
    sbds_cli.add_command(sbds.codegen.cli.cli)
    sbds_cli()
