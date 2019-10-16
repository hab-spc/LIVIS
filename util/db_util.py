""" 
Filename: db_util.py
Authors: Kush
Description: CRUD functions to interact with the database
"""

# imports
import sqlite3
from sqlite3 import Error
import json

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
            return conn
        except Error as e:
            print(e)
            
        return None

    def close_connection(self):
        """ close the connection
        """
        if self.conn != None:
            self.conn.close()

    def new_table(self, name, schema):
        """ create a new table with the given schema
        :param name: name of the new table
        :param schema: the schema as a string
        :return: None
        """
        query = "CREATE TABLE " + str(name) + " (" + str(schema) +");"
        try:
            cur = self.conn.cursor()
            cur.execute(query)
        except:
            print("Error in create table operation")
            self.conn.rollback()

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
            self.conn.rollback


    def update(self, query):
        """ update certain values specified by query
        :param :
        :param :
        """
        pass

    def delete(self, query):
        """
        """
        pass
