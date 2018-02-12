# -*- coding: utf-8 -*-
import click

from sbds.chain.cli import chain
from sbds.checkpoints.cli import checkpoints
from sbds.storages.db.cli import db
from sbds.storages.s3.cli import s3
from sbds.server.cli import server


@click.group(
    short_help=
    'manages storage, retrieval, and querying of the Steem blockchain')
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
sbds.add_command(server)
