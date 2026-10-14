"""
=========================================================
AUTOCARE PRECISION - VALIDATION SUITE TEST SCRIPT
=========================================================
Tests and verifies that phone numbers > 10 digits are rejected,
and that data validation across all tables and CRUD operations
strictly protects the database from invalid inputs.
"""

from app import app
from database import execute_read_query, execute_write_query


def run_tests():
    client = app.test_client()
    print("=========================================================")
    print(" RUNNING COMPREHENSIVE DATA VALIDATION TEST SUITE")
    print("=========================================================\n")

    # TEST 1: Customer Phone with 11 digits (Must be REJECTED)
    print("[TEST 1] Submitting Customer with 11-digit phone '98765432109'...")
    res = client.post("/add_customer", data={
        "name": "Test Client Invalid Phone",
        "phone": "98765432109",
        "email": "invalid@test.com"
    }, follow_redirects=True)
    assert b"cannot exceed 10 digits" in res.data or b"Invalid phone number" in res.data
    # Verify NOT in database
    check = execute_read_query("SELECT * FROM Customer WHERE name = 'Test Client Invalid Phone';", fetch_one=True)
    assert check is None
    print(" -> PASSED: 11-digit phone was rejected and NOT inserted!\n")

    # TEST 2: Customer Phone with letters '98765ABCDE' (Must be REJECTED)
    print("[TEST 2] Submitting Customer with alphabetic phone '98765ABCDE'...")
    res = client.post("/add_customer", data={
        "name": "Test Client Letter Phone",
        "phone": "98765ABCDE",
        "email": "invalid2@test.com"
    }, follow_redirects=True)
    assert b"only numeric digits" in res.data or b"Invalid phone number" in res.data
    check = execute_read_query("SELECT * FROM Customer WHERE name = 'Test Client Letter Phone';", fetch_one=True)
    assert check is None
    print(" -> PASSED: Phone with letters was rejected!\n")

    # TEST 3: Customer Phone with valid 10 digits '9876543210' (Must SUCCEED)
    print("[TEST 3] Submitting Customer with valid 10-digit phone '9876543210'...")
    res = client.post("/add_customer", data={
        "name": "Validation Test Customer",
        "phone": "9876543210",
        "email": "valid@test.com"
    }, follow_redirects=True)
    assert b"registered successfully" in res.data
    check = execute_read_query("SELECT * FROM Customer WHERE name = 'Validation Test Customer';", fetch_one=True)
    assert check is not None
    assert check["phone"] == "9876543210"
    customer_id = check["customer_id"]
    print(f" -> PASSED: 10-digit customer inserted successfully (ID: {customer_id})!\n")

    # TEST 4: Mechanic Phone with 12 digits (Must be REJECTED)
    print("[TEST 4] Submitting Mechanic with 12-digit phone '999999999999'...")
    res = client.post("/add_mechanic", data={
        "name": "Test Invalid Mechanic",
        "specialization": "Engine Specialist",
        "phone": "999999999999",
        "status": "Available"
    }, follow_redirects=True)
    assert b"cannot exceed 10 digits" in res.data or b"Invalid phone number" in res.data
    check = execute_read_query("SELECT * FROM Mechanic WHERE name = 'Test Invalid Mechanic';", fetch_one=True)
    assert check is None
    print(" -> PASSED: 12-digit mechanic phone was rejected!\n")

    # TEST 5: Spare Part with negative price (Must be REJECTED)
    print("[TEST 5] Submitting Spare Part with negative price -150.00...")
    res = client.post("/add_spare_part", data={
        "part_name": "Invalid Brake Disc",
        "price": "-150.00",
        "stock_quantity": "10"
    }, follow_redirects=True)
    assert b"cannot be negative" in res.data or b"positive monetary value" in res.data
    check = execute_read_query("SELECT * FROM Spare_Part WHERE part_name = 'Invalid Brake Disc';", fetch_one=True)
    assert check is None
    print(" -> PASSED: Negative price was rejected!\n")

    # TEST 6: Spare Part with negative stock (Must be REJECTED)
    print("[TEST 6] Submitting Spare Part with negative stock -5...")
    res = client.post("/add_spare_part", data={
        "part_name": "Invalid Oil Filter",
        "price": "450.00",
        "stock_quantity": "-5"
    }, follow_redirects=True)
    assert b"cannot be negative" in res.data
    check = execute_read_query("SELECT * FROM Spare_Part WHERE part_name = 'Invalid Oil Filter';", fetch_one=True)
    assert check is None
    print(" -> PASSED: Negative stock quantity was rejected!\n")

    # TEST 7: Vehicle with short VIN < 11 characters (Must be REJECTED)
    print("[TEST 7] Submitting Vehicle with invalid 5-character VIN 'VIN12'...")
    res = client.post("/add_vehicle", data={
        "customer_id": str(customer_id),
        "registration_no": "TEST99AA1234",
        "vin": "VIN12",
        "make": "BMW",
        "model": "M3",
        "warranty_details": "Active"
    }, follow_redirects=True)
    assert b"VIN must be at least 11 characters" in res.data
    check = execute_read_query("SELECT * FROM Vehicle WHERE registration_no = 'TEST99AA1234';", fetch_one=True)
    assert check is None
    print(" -> PASSED: Short VIN was rejected!\n")

    # TEST 8: Invoice with negative total amount (Must be REJECTED)
    print("[TEST 8] Submitting Invoice with negative amount -500.00...")
    res = client.post("/add_invoice", data={
        "job_card_id": "1",
        "invoice_date": "2026-10-14",
        "total_amount": "-500.00",
        "status": "Unpaid"
    }, follow_redirects=True)
    assert b"cannot be negative" in res.data
    print(" -> PASSED: Negative invoice amount was rejected!\n")

    # Cleanup test customer
    execute_write_query("DELETE FROM Customer WHERE customer_id = %s;", (customer_id,))
    print("=========================================================")
    print(" ALL 8 VALIDATION TESTS PASSED WITH 100% SUCCESS!")
    print("=========================================================")


if __name__ == "__main__":
    run_tests()
