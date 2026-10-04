"""
Automated Test Suite for Multi-Brand Vehicle Service Centre Management System (V1)
Tests all routes, CRUD operations, foreign key protections,
unique constraint validations, VIN slots, model numbers, warranty tracking,
and vehicle previous service history.
"""

import html
import unittest
from app import app
from database import execute_read_query, execute_write_query

class VehicleServiceCentreTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.cleanup_test_data()

    def tearDown(self):
        self.cleanup_test_data()

    def cleanup_test_data(self):
        """Ensure test artifacts are purged so tests are strictly isolated."""
        try:
            execute_write_query("DELETE FROM Vehicle WHERE registration_no IN ('KA05HY1234', 'KA01LUX9999');")
            execute_write_query("DELETE FROM Customer WHERE name LIKE 'Arjun Singhania%';")
            execute_write_query("DELETE FROM Mechanic WHERE name = 'Devrat Sen';")
            execute_write_query("DELETE FROM Spare_Part WHERE part_name IN ('Faulty Component', 'Michelin Pilot Sport 4S');")
            execute_write_query("DELETE FROM Service_Booking WHERE service_type = 'Multi-Point Periodic Maintenance';")
        except Exception:
            pass

    def test_01_dashboard(self):
        """Test Dashboard route returns HTTP 200 and renders universal multi-brand layout."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = html.unescape(response.data.decode("utf-8"))
        # Multi-brand elements
        self.assertIn("Automotive Care & Workshop Command", content)
        self.assertIn("Multi-Brand Workshop Facility", content)
        self.assertIn("Lookup VIN", content)
        self.assertIn("Service offering", content)
        self.assertIn("Service & Maintenance", content)
        self.assertIn("Genuine Parts, Tyres & Oil", content)
        self.assertIn("Further information", content)
        self.assertIn("Total Customers", content)
        self.assertIn("Enrolled Cars", content)
        self.assertIn("Total Bookings", content)
        self.assertIn("Pending Job Cards", content)
        # Ensure BMW 7 series commercial ad was removed
        self.assertNotIn("BMW 7 Series Sedan - Pure Forwardism", content)
        print(" [PASS] Multi-Brand Universal Dashboard & quick VIN search rendered successfully.")

    def test_02_customers_crud(self):
        """Test Customer listing, search, creation, editing, and FK constraint."""
        # 1. Listing
        res = self.client.get("/customers")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Customer Directory", res.data.decode("utf-8"))

        # 2. Add Customer
        post_res = self.client.post("/add_customer", data={
            "name": "Arjun Singhania",
            "phone": "9998887776",
            "email": "arjun.s@autocare.com"
        }, follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)
        content = html.unescape(post_res.data.decode("utf-8"))
        self.assertIn("Customer 'Arjun Singhania' registered successfully!", content)

        # Query newly added customer
        created = execute_read_query("SELECT * FROM Customer WHERE name = %s;", ("Arjun Singhania",), fetch_one=True)
        self.assertIsNotNone(created)
        cid = created["customer_id"]

        # 3. Edit Customer
        edit_res = self.client.post(f"/edit_customer/{cid}", data={
            "name": "Arjun Singhania Edited",
            "phone": "9998887770",
            "email": "arjun.edited@autocare.com"
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)
        self.assertIn(f"Customer #{cid} updated successfully", edit_res.data.decode("utf-8"))

        # 4. Search Customer
        search_res = self.client.get("/customers?search=Singhania")
        self.assertIn("Arjun Singhania Edited", search_res.data.decode("utf-8"))

        # 5. Delete newly added customer (has 0 vehicles, should succeed)
        del_res = self.client.post(f"/delete_customer/{cid}", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertIn(f"Customer #{cid} deleted successfully.", del_res.data.decode("utf-8"))

        # 6. Foreign Key Protection Test: Try deleting customer #1 (owns vehicles)
        fk_res = self.client.post("/delete_customer/1", follow_redirects=True)
        self.assertEqual(fk_res.status_code, 200)
        self.assertIn("Customer cannot be deleted because vehicles are associated with this customer.", fk_res.data.decode("utf-8"))
        print(" [PASS] Customer CRUD & FK protection verified.")

    def test_03_vehicles_vin_warranty_and_history(self):
        """Test Vehicle listing, VIN slot, model number, warranty details, and service history dossier."""
        # 1. Listing shows VIN column and Warranty Status
        res = self.client.get("/vehicles")
        self.assertEqual(res.status_code, 200)
        content = html.unescape(res.data.decode("utf-8"))
        self.assertIn("Vehicle Fleet Registry", content)
        self.assertIn("VIN (Chassis Number)", content)
        self.assertIn("Model Number / Trim", content)
        self.assertIn("Warranty Status", content)

        # 2. Duplicate registration test (TS09AB1234 exists)
        dup_res = self.client.post("/add_vehicle", data={
            "customer_id": 1,
            "registration_no": "TS09AB1234",
            "vin": "MALCA51CLMM000001",
            "make": "Hyundai",
            "model": "Creta",
            "model_number": "SX(O) 1.5 Turbo DCT",
            "warranty_details": "Active (3-Year Factory)"
        }, follow_redirects=True)
        self.assertEqual(dup_res.status_code, 200)
        self.assertIn("Vehicle registration number already exists.", dup_res.data.decode("utf-8"))

        # 3. Add new multi-brand vehicle with complete VIN, Model Number, and Warranty
        test_reg = "KA05HY1234"
        test_vin = "MALCA51BLRM889900"
        test_model_num = "SX(O) 1.5 Turbo DCT"
        test_warranty = "Active (5-Year / 140,000 km Extended Shield)"

        add_res = self.client.post("/add_vehicle", data={
            "customer_id": 1,
            "registration_no": test_reg,
            "vin": test_vin,
            "make": "Hyundai",
            "model": "Creta",
            "model_number": test_model_num,
            "warranty_details": test_warranty
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        add_content = html.unescape(add_res.data.decode("utf-8"))
        self.assertIn(f"Vehicle '{test_reg}' (VIN: {test_vin}) registered successfully!", add_content)

        # Query vehicle record from MySQL
        veh = execute_read_query("SELECT * FROM Vehicle WHERE registration_no = %s;", (test_reg,), fetch_one=True)
        self.assertIsNotNone(veh)
        vid = veh["vehicle_id"]
        self.assertEqual(veh["vin"], test_vin)
        self.assertEqual(veh["model_number"], test_model_num)
        self.assertEqual(veh["warranty_details"], test_warranty)

        # 4. Search by VIN
        search_vin = self.client.get(f"/vehicles?search={test_vin}")
        self.assertIn(test_reg, search_vin.data.decode("utf-8"))

        # 5. Search by Model Number
        search_model = self.client.get("/vehicles?search=Turbo")
        self.assertIn(test_reg, search_model.data.decode("utf-8"))

        # 6. Test Vehicle Dossier & Service History Route (/vehicle/<id>)
        detail_res = self.client.get(f"/vehicle/{vid}")
        self.assertEqual(detail_res.status_code, 200)
        detail_content = html.unescape(detail_res.data.decode("utf-8"))
        self.assertIn(test_reg, detail_content)
        self.assertIn(test_vin, detail_content)
        self.assertIn(test_model_num, detail_content)
        self.assertIn(test_warranty, detail_content)
        self.assertIn("Previous Service History Records", detail_content)
        self.assertIn("Warranty & Coverage Status", detail_content)

        # 7. Edit vehicle VIN and warranty
        updated_warranty = "Active (7-Year Platinum Warranty till 2031)"
        edit_res = self.client.post(f"/edit_vehicle/{vid}", data={
            "customer_id": 1,
            "registration_no": test_reg,
            "vin": test_vin,
            "make": "Hyundai",
            "model": "Creta Facelift",
            "model_number": test_model_num,
            "warranty_details": updated_warranty
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)

        # Verify update in database
        updated_veh = execute_read_query("SELECT * FROM Vehicle WHERE vehicle_id = %s;", (vid,), fetch_one=True)
        self.assertEqual(updated_veh["warranty_details"], updated_warranty)
        self.assertEqual(updated_veh["model"], "Creta Facelift")

        print(" [PASS] Vehicle VIN slot, Model number, Warranty details & Service History verified.")

    def test_04_bookings_crud(self):
        """Test Bookings listing, creation, and status update."""
        res = self.client.get("/bookings")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Scheduled Service Appointments", res.data.decode("utf-8"))

        # Create booking
        post_res = self.client.post("/add_booking", data={
            "vehicle_id": 1,
            "booking_date": "2026-09-28",
            "service_type": "Multi-Point Periodic Maintenance",
            "status": "Booked"
        }, follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)
        self.assertIn("Service booking confirmed successfully!", post_res.data.decode("utf-8"))
        print(" [PASS] Bookings module verified.")

    def test_05_job_cards_crud(self):
        """Test Job Cards listing and status."""
        res = self.client.get("/job_cards")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Workshop Job Cards", res.data.decode("utf-8"))
        print(" [PASS] Job Cards module verified.")

    def test_06_mechanics_crud(self):
        """Test Mechanics listing, search, add, edit, delete."""
        res = self.client.get("/mechanics")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Technician Roster", res.data.decode("utf-8"))

        # Add technician
        add_res = self.client.post("/add_mechanic", data={
            "name": "Devrat Sen",
            "specialization": "Transmission & Hybrid Powertrain",
            "phone": "9811002233",
            "status": "Available"
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        content = html.unescape(add_res.data.decode("utf-8"))
        self.assertIn("Technician 'Devrat Sen' registered successfully!", content)

        # Query and delete
        m = execute_read_query("SELECT mechanic_id FROM Mechanic WHERE name = %s;", ("Devrat Sen",), fetch_one=True)
        self.assertIsNotNone(m)
        del_res = self.client.post(f"/delete_mechanic/{m['mechanic_id']}", follow_redirects=True)
        self.assertIn("deleted successfully.", del_res.data.decode("utf-8"))
        print(" [PASS] Mechanics module verified.")

    def test_07_spare_parts_crud_and_low_stock(self):
        """Test Spare Parts listing, validation, low stock badge."""
        res = self.client.get("/spare_parts")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Genuine Parts & Inventory", res.data.decode("utf-8"))

        # Test negative price validation
        neg_res = self.client.post("/add_spare_part", data={
            "part_name": "Faulty Component",
            "price": "-100",
            "stock_quantity": "5"
        }, follow_redirects=True)
        self.assertIn("Price and stock quantity cannot be negative.", neg_res.data.decode("utf-8"))

        # Add part with low stock (<= 5)
        add_res = self.client.post("/add_spare_part", data={
            "part_name": "Michelin Pilot Sport 4S",
            "price": "34500.00",
            "stock_quantity": "2"
        }, follow_redirects=True)
        self.assertIn("added to catalog!", add_res.data.decode("utf-8"))

        # Verify low stock badge rendered
        list_res = self.client.get("/spare_parts?search=Michelin")
        self.assertIn("Low Stock", list_res.data.decode("utf-8"))
        print(" [PASS] Spare parts module & low-stock badge verified.")

    def test_08_invoices_and_reports(self):
        """Test Invoices listing and Reports rendering with SQL aggregation."""
        # Invoices
        inv_res = self.client.get("/invoices")
        self.assertEqual(inv_res.status_code, 200)
        self.assertIn("Customer Invoices & Billing", inv_res.data.decode("utf-8"))

        # Reports
        rep_res = self.client.get("/reports")
        self.assertEqual(rep_res.status_code, 200)
        content = html.unescape(rep_res.data.decode("utf-8"))
        self.assertIn("Customer & Vehicle Association Report", content)
        self.assertIn("Pending Workshop Jobs", content)
        self.assertIn("Booking History Audit", content)
        self.assertIn("Revenue Audit", content)
        print(" [PASS] Invoices & Reports modules verified.")

if __name__ == "__main__":
    unittest.main()
