"""
=========================================================
VEHICLE SERVICE CENTRE MANAGEMENT SYSTEM
Database Connection & Query Execution Helper (database.py)
=========================================================
This module manages database connections and query executions
using mysql-connector-python and environment variables.
"""

import os
import mysql.connector
from mysql.connector import Error, errorcode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "vehicle_service_centre")


def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    Raises mysql.connector.Error if the connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            collation="utf8mb4_general_ci",
            autocommit=False
        )
        return connection
    except mysql.connector.Error as err:
        print(f"[ERROR] Database connection error: {err}")
        raise err


def execute_read_query(query, params=None, fetch_one=False):
    """
    Executes a SELECT query using parameterized inputs and dictionary cursor.
    Safely closes cursor and connection in a finally block.
    
    :param query: Parameterized SQL string (using %s)
    :param params: Tuple or list of parameters to substitute
    :param fetch_one: If True, returns a single dictionary; otherwise returns list of dictionaries.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"[SQL READ ERROR] Query: {query} | Error: {err}")
        raise err
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def execute_write_query(query, params=None):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    Commits the transaction and returns lastrowid or rowcount.
    Safely handles rollback on failure and closes connections in finally.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        return {
            "lastrowid": cursor.lastrowid,
            "rowcount": cursor.rowcount
        }
    except mysql.connector.Error as err:
        if connection and connection.is_connected():
            connection.rollback()
        print(f"[SQL WRITE ERROR] Query: {query} | Error: {err}")
        raise err
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def test_connection():
    """Utility to test if database connection succeeds."""
    try:
        conn = get_db_connection()
        if conn.is_connected():
            conn.close()
            return True, "Connected successfully."
    except Exception as e:
        return False, str(e)
