""" 
Filename: db_util.py
Authors: Kush
Description: CRUD functions to interact with the database
"""

# imports
from datetime import datetime
import logging
import os
import sqlite3
import sys
from pathlib import Path
from sqlite3 import Error

sys.path.insert(0, str(Path(__file__).resolve().parents[1]) + '/')

# Third party imports
import click

# Project level imports
from config.config import opt, create_table_commands, select_from_table_commands
from constants.genericconstants import DBConstants as DBCONST
from database.db_util import Database

# Module Level Constants
TABLE_NAME = DBCONST.TABLE
CREATE_CMD = create_table_commands
SELECT_CMD = select_from_table_commands

@click.command()
@click.option('--db_path', default=None, help='DB Path to create.')
def create_db(db_path):
    db_path = db_path if db_path else opt.DB_PATH
    if os.path.exists(db_path):
        date_time = datetime.now().strftime("%Y%m%d")
        db_path = db_path.replace('.db', '_{}.db'.format(date_time))
    db = Database(db_path)
    db.execute(operation='create new table', query=CREATE_CMD[TABLE_NAME])
    print('SUCCESS: TABLE CREATED')

    if not os.path.exists(opt.META_DIR):
        os.mkdir(opt.META_DIR)

if __name__ == '__main__':
    create_db()
