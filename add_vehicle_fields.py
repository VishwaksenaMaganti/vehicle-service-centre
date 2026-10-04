"""
Migration script to add VIN number, model number, and warranty details
to the Vehicle table and populate realistic multi-brand data.
"""
from database import execute_write_query, execute_read_query

# 1. Add columns if not present
existing_cols = [c['Field'] for c in execute_read_query("DESCRIBE Vehicle;")]

if "vin" not in existing_cols:
    execute_write_query("ALTER TABLE Vehicle ADD COLUMN vin VARCHAR(30) DEFAULT NULL;")
    print("Added 'vin' column.")

if "model_number" not in existing_cols:
    execute_write_query("ALTER TABLE Vehicle ADD COLUMN model_number VARCHAR(50) DEFAULT NULL;")
    print("Added 'model_number' column.")

if "warranty_details" not in existing_cols:
    execute_write_query("ALTER TABLE Vehicle ADD COLUMN warranty_details VARCHAR(100) DEFAULT 'Standard Warranty Active';")
    print("Added 'warranty_details' column.")

# 2. Update existing vehicles to be clean multi-brand (BMW, Porsche, Hyundai, Toyota, Honda, etc.)
vehicles_data = [
    (1, "BMW", "7 Series Sedan", "WBA73EJ04PCH91823", "740Li xDrive (G70)", "Active · Comprehensive 5-Year Inclusive Package"),
    (2, "Porsche", "911 Carrera", "WP0AA2A94NS240192", "992 Carrera 4S", "Active · Porsche Approved Warranty till Oct 2027"),
    (3, "Hyundai", "Creta", "MALC381CLPM102948", "SX(O) 1.5 Turbo DCT", "Active · 3-Year / Unlimited KM Factory Warranty"),
    (4, "Toyota", "Fortuner", "MBJ11EB84MN492019", "2.8 4x4 AT Legender", "Active · Toyota Shield Protection till Dec 2028"),
    (5, "Honda", "City", "MAKGM668LNA390123", "ZX 1.5 i-VTEC CVT", "Active · 5-Year Comprehensive Warranty")
]

for vid, make, model, vin, model_no, warranty in vehicles_data:
    execute_write_query("""
        UPDATE Vehicle 
        SET make = %s, model = %s, vin = %s, model_number = %s, warranty_details = %s 
        WHERE vehicle_id = %s;
    """, (make, model, vin, model_no, warranty, vid))

print("Updated existing vehicles with VIN, Model Number, and Warranty details.")

# Verify
rows = execute_read_query("SELECT vehicle_id, registration_no, vin, make, model, model_number, warranty_details FROM Vehicle;")
for r in rows:
    print(r)
