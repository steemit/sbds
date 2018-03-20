# -*- coding: utf-8 -*-
import click

import structlog
from .serve import run

logger = structlog.get_logger(__name__)


@click.group()
def server():
    """HTTP server for answering DB queries"""


# Development server
@server.command(name='serve')
@click.option('--host', type=click.STRING, default='localhost', help='host')
@click.option('--port', type=click.INT, default=8080, help='host TCP port')
def server_command(host, port):
    """server"""
    run(host, port)
