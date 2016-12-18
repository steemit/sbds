import os
import mysql.connector
from mysql.connector import errorcode

from url import URL

# support DATABASE_URL ENV variable parsing
db_url = URL.from_env()

if db_url:
    db_config = db_url.translate_connect_args()

else:
    db_config = {
  'user': os.environ.get('MYSQL_USERNAME','steemit'),
  'password': os.environ.get('MYSQL_PASSWORD', 'password'),
  'host': os.environ.get('MYSQL_HOST','127.0.0.1'),
  'database': os.environ.get('MYSQL_DATABASE','steem')
}

db_config.update(
    {
        'raise_on_warnings': True,
        'use_pure': True,
        'autocommit': True}
)

cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

add_block_sql='INSERT INTO Blocks (raw) VALUES (%(raw)s)'

def get_tables(tables_file='tables.sql'):
    with open('tables.sql','r') as f:
        tables = f.read()
    return tables

def create_database(cursor, database):
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {}".format(database))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))

def drop_database(cursor, database):
    try:
        cursor.execute(
            "DROP DATABASE IF EXISTS {} ".format(database))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))

def create_tables(cursor, database, tables):
    try:
        cnx.database = database
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor, database)
            cnx.database = database
        else:
            pass
    cursor.execute(tables)

def add_block(cursor, block, add_block_sql=add_block_sql):
    cursor.execute(add_block_sql, dict(raw=block))
