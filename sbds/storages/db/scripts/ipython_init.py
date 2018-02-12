# coding=utf-8
import os

from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db.tables import Session
from sbds.storages.db.utils import configure_engine

db_url = os.environ['DATABASE_URL']
rpc_url = os.environ['STEEMD_HTTP_URL']

engine_config = configure_engine(db_url)
engine = engine_config.engine
session = Session(bind=engine)
client = SimpleSteemAPIClient(url=rpc_url)
