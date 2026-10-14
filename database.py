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

import time
from datetime import datetime
from collections import deque

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "vehicle_service_centre")

# Thread-safe buffer for recent SQL executions
RECENT_SQL_LOGS = deque(maxlen=100)
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql_execution.log")


def log_sql_execution(query_type, query, params, duration_ms, rowcount=None, lastrowid=None, error=None):
    """
    Logs SQL execution to terminal (ANSI color), appends to sql_execution.log,
    and caches in memory for the web live monitor.
    """
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    cleaned_query = " ".join(query.strip().split())

    log_entry = {
        "timestamp": timestamp_str,
        "type": query_type,
        "query": cleaned_query,
        "params": str(params) if params else None,
        "duration_ms": round(duration_ms, 2),
        "rowcount": rowcount,
        "lastrowid": lastrowid,
        "error": str(error) if error else None,
        "status": "ERROR" if error else "OK"
    }
    RECENT_SQL_LOGS.appendleft(log_entry)

    # ANSI Colors
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    # Terminal box formatting (ASCII safe for Windows console)
    if error:
        print(f"\n{RED}{BOLD}+-- [SQL ERROR] {timestamp_str} ------------------------------------------{RESET}")
        print(f"{RED}| QUERY    : {cleaned_query}{RESET}")
        if params:
            print(f"{RED}| PARAMS   : {params}{RESET}")
        print(f"{RED}| ERROR    : {error}{RESET}")
        print(f"{RED}| DURATION : {duration_ms:.2f} ms | STATUS: ROLLBACK{RESET}")
        print(f"{RED}+--------------------------------------------------------------------------+{RESET}\n")
    else:
        badge_color = GREEN if query_type == "WRITE" else CYAN
        type_label = "TRANSACTION WRITE (COMMIT)" if query_type == "WRITE" else "READ QUERY"
        
        print(f"\n{badge_color}{BOLD}+-- [SQL {type_label}] {timestamp_str} -----------------------------{RESET}")
        print(f"{badge_color}|{RESET} {BOLD}QUERY   :{RESET} {cleaned_query}")
        if params:
            print(f"{badge_color}|{RESET} {GRAY}PARAMS  :{RESET} {params}")
        
        info_line = f"{duration_ms:.2f} ms"
        if rowcount is not None:
            info_line += f" | ROWS: {rowcount}"
        if lastrowid:
            info_line += f" | LAST_INSERT_ID: {lastrowid}"
            
        print(f"{badge_color}|{RESET} {YELLOW}DURATION:{RESET} {info_line} | {GREEN}STATUS: SUCCESS{RESET}")
        print(f"{badge_color}+--------------------------------------------------------------------------+{RESET}")

    # Append to sql_execution.log file for separate live terminal window
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            status_text = f"ERROR: {error}" if error else f"OK ({duration_ms:.2f}ms)"
            f.write(f"[{timestamp_str}] [{query_type}] {cleaned_query} | PARAMS: {params} | {status_text}\n")
    except Exception:
        pass


def get_recent_sql_logs():
    """Returns a list of recent SQL execution dictionaries."""
    return list(RECENT_SQL_LOGS)


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
    """
    connection = None
    cursor = None
    t0 = time.perf_counter()
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch_one:
            result = cursor.fetchone()
            rows_cnt = 1 if result else 0
        else:
            result = cursor.fetchall()
            rows_cnt = len(result)
            
        dt = (time.perf_counter() - t0) * 1000
        log_sql_execution("READ", query, params, dt, rowcount=rows_cnt)
        return result
    except mysql.connector.Error as err:
        dt = (time.perf_counter() - t0) * 1000
        log_sql_execution("READ", query, params, dt, error=err)
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
    """
    connection = None
    cursor = None
    t0 = time.perf_counter()
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        last_id = cursor.lastrowid
        cnt = cursor.rowcount
        dt = (time.perf_counter() - t0) * 1000
        log_sql_execution("WRITE", query, params, dt, rowcount=cnt, lastrowid=last_id)
        return {
            "lastrowid": last_id,
            "rowcount": cnt
        }
    except mysql.connector.Error as err:
        dt = (time.perf_counter() - t0) * 1000
        if connection and connection.is_connected():
            connection.rollback()
        log_sql_execution("WRITE", query, params, dt, error=err)
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
