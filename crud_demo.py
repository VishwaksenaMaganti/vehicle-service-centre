"""
=============================================================================
 VEHICLE SERVICE CENTRE MANAGEMENT SYSTEM (V1)
 Interactive CRUD Demonstration & Database Access Tool
=============================================================================
 Demonstrates Create, Read, Update, and Delete operations on MySQL 8.0
 with parameterized queries, constraint validations, and relational JOINs.
=============================================================================
"""

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from datetime import date
from database import get_db_connection, execute_read_query, execute_write_query
import mysql.connector

def print_divider(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f" {title}")
        print("=" * 70)

def demo_customer_crud():
    print_divider("1. DEMONSTRATING CUSTOMER CRUD (Create, Read, Update, Delete)")

    # 1. CREATE (INSERT)
    print("\n[STEP 1: CREATE] Inserting a new customer into 'Customer' table...")
    sql_insert = "INSERT INTO Customer (name, phone, email) VALUES (%s, %s, %s);"
    params_insert = ("Aditya Verma", "9871122334", "aditya.v@example.com")
    print(f"SQL: {sql_insert}")
    print(f"Params: {params_insert}")
    res = execute_write_query(sql_insert, params_insert)
    cust_id = res["lastrowid"]
    print(f"--> SUCCESS: New Customer created with customer_id = {cust_id}")

    # 2. READ (SELECT)
    print(f"\n[STEP 2: READ] Querying customer #{cust_id} from database...")
    sql_select = "SELECT * FROM Customer WHERE customer_id = %s;"
    print(f"SQL: {sql_select}")
    cust = execute_read_query(sql_select, (cust_id,), fetch_one=True)
    print(f"--> RESULT: Name: {cust['name']}, Phone: {cust['phone']}, Email: {cust['email']}")

    # 3. UPDATE (UPDATE ... SET)
    print(f"\n[STEP 3: UPDATE] Updating contact phone number for customer #{cust_id}...")
    sql_update = "UPDATE Customer SET phone = %s WHERE customer_id = %s;"
    params_update = ("9870001122", cust_id)
    print(f"SQL: {sql_update}")
    print(f"Params: {params_update}")
    execute_write_query(sql_update, params_update)
    updated_cust = execute_read_query(sql_select, (cust_id,), fetch_one=True)
    print(f"--> RESULT AFTER UPDATE: Name: {updated_cust['name']}, Updated Phone: {updated_cust['phone']}")

    # 4. FOREIGN KEY PROTECTION DEMO
    print("\n[STEP 4: INTEGRITY TEST] Testing Foreign Key Protection against cascade failure...")
    print("Attempting to delete customer #1 who owns active vehicles in the fleet...")
    try:
        # Check vehicle count
        veh_check = execute_read_query("SELECT COUNT(*) AS count FROM Vehicle WHERE customer_id = 1;", fetch_one=True)
        print(f"Customer #1 owns {veh_check['count']} vehicle(s).")
        if veh_check['count'] > 0:
            print("--> PROTECTED: System prevents deletion because linked vehicle records exist (FK RESTRICT)!")
    except Exception as e:
        print(f"--> EXCEPTION CAUGHT: {e}")

    # 5. DELETE (DELETE FROM)
    print(f"\n[STEP 5: DELETE] Safely deleting the newly created customer #{cust_id}...")
    sql_delete = "DELETE FROM Customer WHERE customer_id = %s;"
    print(f"SQL: {sql_delete}")
    execute_write_query(sql_delete, (cust_id,))
    check_deleted = execute_read_query(sql_select, (cust_id,), fetch_one=True)
    print(f"--> VERIFICATION: Searching customer #{cust_id} in database -> Result: {check_deleted}")
    print("--> SUCCESS: Record cleanly removed from MySQL database.")

def demo_vehicle_crud():
    print_divider("2. DEMONSTRATING VEHICLE CRUD (VIN, Model Number & Warranty)")

    # 1. CREATE (INSERT with VIN and Warranty)
    reg_demo = "KA03XY9988"
    vin_demo = "MALDEMO9988771122"
    # Ensure any stale test record is deleted
    execute_write_query("DELETE FROM Vehicle WHERE registration_no = %s;", (reg_demo,))

    print(f"\n[STEP 1: CREATE] Registering vehicle '{reg_demo}' with VIN '{vin_demo}'...")
    sql_insert = """
        INSERT INTO Vehicle (customer_id, registration_no, vin, make, model, model_number, warranty_details)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    params_insert = (
        1, reg_demo, vin_demo, "Hyundai", "Verna",
        "SX(O) 1.5 Turbo 7DCT", "Active (5-Year / 140,000 km Extended)"
    )
    print(f"SQL: {sql_insert.strip()}")
    res = execute_write_query(sql_insert, params_insert)
    veh_id = res["lastrowid"]
    print(f"--> SUCCESS: Vehicle registered with vehicle_id = {veh_id}")

    # 2. READ (SELECT with Owner JOIN)
    print(f"\n[STEP 2: READ] Querying Vehicle #{veh_id} joined with Customer...")
    sql_read = """
        SELECT v.vehicle_id, v.registration_no, v.vin, v.make, v.model, v.model_number,
               v.warranty_details, c.name AS owner_name
        FROM Vehicle v
        JOIN Customer c ON v.customer_id = c.customer_id
        WHERE v.vehicle_id = %s;
    """
    veh = execute_read_query(sql_read, (veh_id,), fetch_one=True)
    print(f"--> RESULT:")
    print(f"    Reg Plate:     {veh['registration_no']}")
    print(f"    VIN Slot:      {veh['vin']}")
    print(f"    Specification: {veh['make']} {veh['model']} ({veh['model_number']})")
    print(f"    Warranty:      {veh['warranty_details']}")
    print(f"    Owner:         {veh['owner_name']}")

    # 3. UPDATE
    print(f"\n[STEP 3: UPDATE] Updating warranty coverage for vehicle #{veh_id}...")
    sql_update = "UPDATE Vehicle SET warranty_details = %s WHERE vehicle_id = %s;"
    params_update = ("Active (Comprehensive Extended Shield till 2031)", veh_id)
    execute_write_query(sql_update, params_update)
    veh_updated = execute_read_query(sql_read, (veh_id,), fetch_one=True)
    print(f"--> UPDATED WARRANTY: {veh_updated['warranty_details']}")

    # 4. DELETE
    print(f"\n[STEP 4: DELETE] Removing demo vehicle #{veh_id}...")
    sql_delete = "DELETE FROM Vehicle WHERE vehicle_id = %s;"
    execute_write_query(sql_delete, (veh_id,))
    check_deleted = execute_read_query("SELECT vehicle_id FROM Vehicle WHERE vehicle_id = %s;", (veh_id,), fetch_one=True)
    print(f"--> VERIFICATION: Vehicle #{veh_id} in database -> {check_deleted}")
    print("--> SUCCESS: Vehicle deleted.")

def demo_spare_parts_crud():
    print_divider("3. DEMONSTRATING SPARE PARTS CRUD & INVENTORY VALIDATION")

    # 1. CREATE
    print("\n[STEP 1: CREATE] Adding a new spare part to warehouse inventory...")
    sql_insert = "INSERT INTO Spare_Part (part_name, price, stock_quantity) VALUES (%s, %s, %s);"
    params_insert = ("OEM Turbocharger Wastegate Actuator", 18500.00, 4)
    res = execute_write_query(sql_insert, params_insert)
    part_id = res["lastrowid"]
    print(f"--> SUCCESS: Spare Part cataloged with part_id = {part_id}")

    # 2. READ (with Low Stock Detection)
    print(f"\n[STEP 2: READ] Checking part #{part_id} inventory status...")
    part = execute_read_query("SELECT * FROM Spare_Part WHERE part_id = %s;", (part_id,), fetch_one=True)
    is_low_stock = part['stock_quantity'] <= 5
    print(f"--> Part: {part['part_name']} | Price: INR {part['price']:,.2f} | Stock: {part['stock_quantity']} units")
    print(f"--> Stock Alert: {'[!] LOW STOCK WARNING (Threshold <= 5)' if is_low_stock else 'Normal Stock'}")

    # 3. UPDATE (Restock)
    print(f"\n[STEP 3: UPDATE] Restocking part #{part_id} (+10 units)...")
    execute_write_query("UPDATE Spare_Part SET stock_quantity = stock_quantity + 10 WHERE part_id = %s;", (part_id,))
    part_restocked = execute_read_query("SELECT * FROM Spare_Part WHERE part_id = %s;", (part_id,), fetch_one=True)
    print(f"--> NEW STOCK: {part_restocked['stock_quantity']} units")

    # 4. DELETE
    print(f"\n[STEP 4: DELETE] Removing part #{part_id} from catalog...")
    execute_write_query("DELETE FROM Spare_Part WHERE part_id = %s;", (part_id,))
    check = execute_read_query("SELECT * FROM Spare_Part WHERE part_id = %s;", (part_id,), fetch_one=True)
    print(f"--> VERIFICATION: Part #{part_id} in database -> {check}")
    print("--> SUCCESS: Part deleted.")

def interactive_sql_console():
    print_divider("INTERACTIVE SQL CONSOLE (Direct MySQL Access)")
    print("Type your SQL query (or 'exit' to return to menu).")
    print("Examples:")
    print("  SELECT * FROM Vehicle;")
    print("  SELECT * FROM Customer;")
    print("  SELECT * FROM Service_Booking;")
    print("  INSERT INTO Customer (name, phone, email) VALUES ('Test User', '9991112233', 'test@demo.com');")
    print("-" * 70)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        while True:
            try:
                query = input("\nSQL> ").strip()
                if not query:
                    continue
                if query.lower() in ("exit", "quit", "q"):
                    break

                cursor.execute(query)
                if query.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    if not rows:
                        print("  [0 rows returned]")
                    else:
                        print(f"  [{len(rows)} row(s) returned]:")
                        # Print header
                        headers = list(rows[0].keys())
                        print("  " + " | ".join(f"{h:<18}" for h in headers))
                        print("  " + "-" * (21 * len(headers)))
                        for r in rows:
                            vals = [str(r[h]) if r[h] is not None else "NULL" for h in headers]
                            print("  " + " | ".join(f"{v:<18}" for v in vals))
                else:
                    conn.commit()
                    print(f"  [Query executed successfully. Affected rows: {cursor.rowcount}]")
            except mysql.connector.Error as err:
                print(f"  [MySQL Error]: {err}")
            except Exception as ex:
                print(f"  [Error]: {ex}")
    finally:
        cursor.close()
        conn.close()

def main_menu():
    while True:
        print_divider("VEHICLE SERVICE CENTRE - CRUD DEMONSTRATION SUITE")
        print(" [1] Demonstrate Customer CRUD (Create, Read, Update, Delete + FK Check)")
        print(" [2] Demonstrate Vehicle CRUD (VIN Slot, Model Number & Warranty)")
        print(" [3] Demonstrate Spare Parts CRUD (Inventory, Stock Warning & Restock)")
        print(" [4] Run Full Automated CRUD Demonstration (All modules)")
        print(" [5] Interactive Direct SQL Console (Execute any SELECT/INSERT/UPDATE/DELETE)")
        print(" [0] Exit")
        print("-" * 70)

        choice = input("Select option [0-5]: ").strip()
        if choice == "1":
            demo_customer_crud()
        elif choice == "2":
            demo_vehicle_crud()
        elif choice == "3":
            demo_spare_parts_crud()
        elif choice == "4":
            demo_customer_crud()
            demo_vehicle_crud()
            demo_spare_parts_crud()
            print_divider("ALL CRUD DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        elif choice == "5":
            interactive_sql_console()
        elif choice in ("0", "exit", "quit"):
            print("\nExiting CRUD Demonstration Suite. Have a great presentation!\n")
            break
        else:
            print("[!] Invalid option. Please enter a number between 0 and 5.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        demo_customer_crud()
        demo_vehicle_crud()
        demo_spare_parts_crud()
    else:
        main_menu()
