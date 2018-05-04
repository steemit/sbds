# -*- coding: utf-8 -*-
import click
import structlog

from sbds.storages.db.tasks import task_init_db_if_required
from sbds.storages.db.tasks import task_collect_missing_block_nums
from sbds.storages.db.tasks import task_load_account_names
from sbds.storages.db.tasks import task_add_missing_blocks

logger = structlog.get_logger(__name__)


@click.command()
@click.option(
    '--database_url',
    type=str,
    envvar='DATABASE_URL',
    help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default'
)
@click.option(
    '--legacy_database_url',
    type=str,
    envvar='LEGACY_DATABASE_URL',
    help='Database connection URL in RFC-1738 format, read from "LEGACY_DATABASE_URL" ENV var by default'
)
@click.option(
    '--steemd_http_url',
    metavar='STEEMD_HTTP_URL',
    envvar='STEEMD_HTTP_URL',
    help='Steemd HTTP server URL')
@click.option('--start_block', type=click.INT, default=1)
@click.option('--end_block', type=click.INT, default=-1)
@click.option('--accounts_file', type=click.Path(dir_okay=False, exists=True))
@click.option('--concurrency', type=click.INT, default=5)
@click.option('--jsonrpc_batch_size', type=click.INT, default=30)
def populate(database_url, legacy_database_url, steemd_http_url,
             start_block, end_block, accounts_file, concurrency, jsonrpc_batch_size):
    _populate(
        database_url,
        legacy_database_url,
        steemd_http_url,
        start_block,
        end_block,
        accounts_file,
        concurrency,
        jsonrpc_batch_size)


def _populate(database_url, legacy_database_url, steemd_http_url,
              start_block, end_block, accounts_file, concurrency, jsonrpc_batch_size):

    # init db if required

    logger.info('Initialising db if required',)
    task_init_db_if_required(database_url=legacy_database_url)

    # preload accounts file
    if accounts_file:
        logger.info('Preloading account names', accounts_file=accounts_file)
        task_load_account_names(database_url=database_url,
                                accounts_file=accounts_file)
    else:
        logger.info('No accounts file provided...skipping ', accounts_file=accounts_file)

    # collect missing block nums
    logger.info(f'Building list of blocks missing from db',
                start_block=start_block, end_block=end_block)

    missing_exising_results = task_collect_missing_block_nums(database_url=database_url,
                                                              steemd_http_url=steemd_http_url,
                                                              start_block=start_block,
                                                              end_block=end_block)

    # add missing blocks and operations
    logger.info('Adding missing blocks and operations to db')
    task_add_missing_blocks(database_url=database_url,
                            steemd_http_url=steemd_http_url,
                            concurrency=concurrency,
                            num_procs=None,
                            jsonrpc_batch_size=jsonrpc_batch_size,
                            missing_block_nums=missing_exising_results['missing_block_nums'],
                            existing_count=missing_exising_results['existing_count'],
                            missing_count=missing_exising_results['missing_count'],
                            range_count=missing_exising_results['range_count'])

    # add new blocks
    logger.info('Streaming new blocks and operations to db')


if __name__ == '__main__':
    populate()
