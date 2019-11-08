""" 
Filename: db_util.py
Authors: Kush
Description: CRUD functions to interact with the database
"""

# imports
import os
import sqlite3
import sys
from pathlib import Path
from sqlite3 import Error

sys.path.insert(0, str(Path(__file__).resolve().parents[1]) + '/')

# Third party imports
import click

# Project level imports
from config.config import opt, create_table_commands

# Module Level Constants
DB_PATH = opt.db_path
CREATE_CMD = create_table_commands

@click.command()
@click.option('--db_path', default=None, help='DB Path to create.')
def create_db(db_path):
    db_path = db_path if db_path else DB_PATH
    if not os.path.exists(db_path):
        db = Database(db_path)
        db.execute(operation='create new table', query=CREATE_CMD['date_sampled'])
        print('SUCCESS: TABLE CREATED')
    else:
        print("FAILED: TABLE ALREADY CREATED")

class Database:
    """ Database instance for CRUD interaction
    """
    def __init__(self, db_path):
        """ construct the database 
        :param db_path: path to the database
        """
        self.conn = self.create_connection(db_path)

    def create_connection(self, db_path):
        """ create a db connection to database
	    :param db_path: database file path
	    :return: Connection object or None
	    """
        try:
            conn = sqlite3.connect(db_path)
            print('SUCCESS: Table Connected')
            return conn
        except Error as e:
            print(e)
            
        return None

    def close_connection(self):
        """ close the connection
        """
        if self.conn != None:
            self.conn.close()
    
    def execute(self, operation, query):
        """ execute the given query
        :param operation: caller function's name
        :param query: query to be executed
        """
        try:
            cur = self.conn.cursor()
            cur.execute(query)
        except:
            print("Error in " + str(operation)+ " operation")
            self.conn.rollback()

    def new_table(self, name, schema):
        """ create a new table with the given schema
        :param name: name of the new table
        :param schema: the schema as a string
        :return: None
        """
        query = "CREATE TABLE " + str(name) + " (" + str(schema) +");"
        self.execute("create new table", query)

    def create(self, query, data):
        """ create rows in table from the given data
        :param query: the Insert query as a string
        :param data: a list of row tuples to be inserted
        :return: None
        """
        try:
            cur = self.conn.cursor()
            cur.executemany(query, data)
        except:
            print("error in insert operation")
            self.conn.rollback()

    def read(self, table_name, cols_needed="*", conditions=None):
        """ get all rows, or all rows specified by the query
        :param table_name: name of the table to select from
        :param cols_needed: string with comma separated list of cols needed, defaults to *
        :param conditions: string with conditions
        :return: result table
        """
        if conditions == None:
            query = "SELECT " + cols_needed + " FROM " + table_name
        else:
            query = "SELECT " + cols_needed + " FROM " + table_name + " " + conditions
        
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            return cur.fetchall()
        except:
            print("error in select operation")
            self.conn.rollback()


    def update(self, table_name, new_vals, prim_key_id):
        """ update certain values specified by query
        :param table_name: name of th table to update
        :param new_vals: a dict with attributes as keys, and
                         values as values
        :param prim_key_id: key value pair as list of size 2 
                         primary key identifier for row to update
        :return: None
        """
        query = "UPDATE " + table_name + " SET "
        for key in new_vals.keys():
            query += str(key) \
                    + " " \
                    + str(new_vals[key]) \
                    + " , "\

        # remove last comma, and space
        query = query[:len(query) - 3]
        query += " WHERE " \
                + str(prim_key_id[0]) \
                + " = " \
                + str(prim_key_id[1]) \

        # execute the query
        self.execute("update", query)

    def delete(self, table_name, prim_key_id):
        """ delete a row from specified table, and prim key value
        :param table_name: name of the table to delete from 
        :param prim_key_id: key value pair as list of size 2 
                         primary key identifier for row to update
        :return: None
        """
        query = "DELETE FROM " \
                + table_name \
                + " WHERE " \
                + str(prim_key_id[0]) \
                + " = " \
                + str(prim_key_id[1]) \

        # execute the query
        self.execute("delete", query)

if __name__ == '__main__':
    create_db()