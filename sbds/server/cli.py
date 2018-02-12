# -*- coding: utf-8 -*-
import click

import sbds.sbds_logging
from sbds.server.serve import run

logger = sbds.sbds_logging.getLogger(__name__)


@click.group()
def server():
    """HTTP server for answering DB queries"""
    pass


# Development server
@server.command(name='serve')
@click.option('--host', type=click.STRING, default='localhost', help='host')
@click.option('--port', type=click.INT, default=8080, help='host TCP port')
def server_command(host, port):
    """server"""
    run(host, port)
