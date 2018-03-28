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
@click.option('--http_host',
              type=click.STRING,
              envvar='HTTP_HOST',
              metavar='HTTP_HOST',
              default='localhost',
              required=True,
              help='host')
@click.option('--http_port',
              type=click.INT,
              envvar='HTTP_PORT',
              metavar='HTTP_PORT',
              default=8080,
              required=True,
              help='host TCP port')
@click.option('--http_client_max_tcp_conn',
              type=click.INT,
              envvar='HTTP_CLIENT_MAX_TCP_CONN',
              metavar='HTTP_CLIENT_MAX_TCP_CONN',
              required=True,
              default=100)
@click.option(
    '--http_client_timeout',
    type=click.INT,
    envvar='HTTP_CLIENT_TIMEOUT',
    metavar='HTTP_CLIENT_TIMEOUT',
    required=True,
    default=3)
@click.option(
    '--database_url',
    type=click.STRING,
    envvar='DATABASE_URL',
    required=True,
    help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default'
)
@click.option(
    '--steemd_http_url',
    type=click.STRING,
    metavar='STEEMD_HTTP_URL',
    envvar='STEEMD_HTTP_URL',
    required=True)
def server_command(http_host,
                   http_port,
                   http_client_max_tcp_conn,
                   http_client_timeout,
                   database_url,
                   steemd_http_url):
    """server"""
    run(http_host,
        http_port,
        http_client_max_tcp_conn=http_client_max_tcp_conn,
        http_client_timeout=http_client_timeout,
        database_url=database_url,
        steemd_http_url=steemd_http_url)
