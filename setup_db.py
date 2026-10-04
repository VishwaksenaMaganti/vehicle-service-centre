"""
=========================================================
Database Initialization and Health Check Script
=========================================================
This script tests the MySQL connection, inspects existing tables,
and can optionally execute vehicle_service_centre.sql if needed.
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "vehicle_service_centre")

def check_and_setup_database():
    print("=========================================================")
    print(" Checking MySQL Connection & Database Setup")
    print("=========================================================")
    print(f" Connecting to MySQL at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        print(" [OK] Successfully authenticated with MySQL server.")

        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE %s;", (DB_NAME,))
        exists = cursor.fetchone()
        if not exists:
            print(f" [INFO] Database '{DB_NAME}' does not exist. Creating...")
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f" [OK] Created database '{DB_NAME}'.")
        else:
            print(f" [OK] Database '{DB_NAME}' exists.")

        cursor.close()
        conn.close()

        # Connect directly to database and check tables
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [t[0] for t in cursor.fetchall()]
        print(f" [INFO] Found {len(tables)} tables: {', '.join(tables)}")

        required_tables = [
            "customer", "vehicle", "service_booking",
            "job_card", "mechanic", "spare_part", "invoice"
        ]
        
        tables_lower = [t.lower() for t in tables]
        missing = [t for t in required_tables if t not in tables_lower]

        if missing:
            print(f" [WARN] Missing tables: {missing}. Importing vehicle_service_centre.sql...")
            sql_file = "vehicle_service_centre.sql"
            if os.path.exists(sql_file):
                with open(sql_file, "r", encoding="utf-8") as f:
                    statements = f.read().split(";")
                    for stmt in statements:
                        stmt = stmt.strip()
                        if stmt:
                            cursor.execute(stmt)
                conn.commit()
                print(" [OK] Imported schema and sample data successfully.")
            else:
                print(f" [ERROR] Could not find '{sql_file}' to import.")
        else:
            print(" [OK] All required tables are present.")
            for t in ["Customer", "Vehicle", "Service_Booking", "Job_Card", "Mechanic", "Spare_Part", "Invoice"]:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {t};")
                    count = cursor.fetchone()[0]
                    print(f"      - {t}: {count} rows")
                except Exception as e:
                    pass

        cursor.close()
        conn.close()
        print("\n [SUCCESS] Database is healthy and ready for the web application!")
        print("=========================================================")

    except mysql.connector.Error as err:
        print(f"\n [ERROR] MySQL Error: {err}")
        print(" Please verify your .env file credentials and that MySQL is running.")

if __name__ == "__main__":
    check_and_setup_database()
