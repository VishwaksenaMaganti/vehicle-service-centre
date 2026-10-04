"""
=========================================================
VEHICLE SERVICE CENTRE MANAGEMENT SYSTEM (Version 1)
College DBMS Project
=========================================================
Backend: Python 3 + Flask
Database: MySQL 8 (vehicle_service_centre)
Connector: mysql-connector-python
"""

import os
import time
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify, send_from_directory
import mysql.connector
from dotenv import load_dotenv

from database import (
    execute_read_query,
    execute_write_query,
    test_connection
)

# Load environment configuration
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "college-dbms-project-default-secret-key-2026")


# =========================================================
# DASHBOARD MODULE
# =========================================================
@app.route("/")
@app.route("/dashboard")
def dashboard():
    """
    Displays the executive command center with:
    - 8 core KPIs calculated via real SQL COUNT & SUM queries.
    - Recent service bookings with Customer and Vehicle JOINs.
    - Pending workshop jobs currently in the bays.
    """
    try:
        # SQL COUNT and SUM statistics queries
        cust_row = execute_read_query("SELECT COUNT(*) AS total FROM Customer", fetch_one=True)
        veh_row = execute_read_query("SELECT COUNT(*) AS total FROM Vehicle", fetch_one=True)
        book_row = execute_read_query("SELECT COUNT(*) AS total FROM Service_Booking", fetch_one=True)
        pending_jobs_row = execute_read_query("SELECT COUNT(*) AS total FROM Job_Card WHERE status = 'Pending'", fetch_one=True)
        mech_row = execute_read_query("SELECT COUNT(*) AS total FROM Mechanic WHERE status = 'Available'", fetch_one=True)
        parts_row = execute_read_query("SELECT COUNT(*) AS total FROM Spare_Part", fetch_one=True)
        unpaid_inv_row = execute_read_query("SELECT COUNT(*) AS total FROM Invoice WHERE status = 'Unpaid'", fetch_one=True)
        revenue_row = execute_read_query("SELECT COALESCE(SUM(total_amount), 0.0) AS total_revenue FROM Invoice WHERE status = 'Paid'", fetch_one=True)

        stats = {
            "total_customers": cust_row["total"] if cust_row else 0,
            "total_vehicles": veh_row["total"] if veh_row else 0,
            "total_bookings": book_row["total"] if book_row else 0,
            "pending_jobs": pending_jobs_row["total"] if pending_jobs_row else 0,
            "available_mechanics": mech_row["total"] if mech_row else 0,
            "total_spare_parts": parts_row["total"] if parts_row else 0,
            "unpaid_invoices": unpaid_inv_row["total"] if unpaid_inv_row else 0,
            "paid_revenue": float(revenue_row["total_revenue"]) if revenue_row else 0.0
        }

        # Recent Bookings (demonstrating SQL 3-table JOIN and ORDER BY)
        recent_bookings_sql = """
            SELECT sb.booking_id, sb.booking_date, sb.service_type, sb.status,
                   v.vehicle_id, v.registration_no, v.vin, v.make, v.model,
                   c.name AS customer_name, c.phone AS customer_phone
            FROM Service_Booking sb
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            ORDER BY sb.booking_date DESC, sb.booking_id DESC
            LIMIT 5;
        """
        recent_bookings = execute_read_query(recent_bookings_sql)

        # Pending Workshop Jobs (demonstrating SQL 4-table JOIN with WHERE filter)
        pending_jobs_sql = """
            SELECT jc.job_card_id, jc.job_description, jc.status,
                   v.vehicle_id, v.registration_no,
                   c.name AS customer_name
            FROM Job_Card jc
            JOIN Service_Booking sb ON jc.booking_id = sb.booking_id
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            WHERE jc.status = 'Pending'
            ORDER BY jc.job_card_id DESC
            LIMIT 5;
        """
        pending_jobs = execute_read_query(pending_jobs_sql)

        return render_template(
            "index.html",
            active_page="dashboard",
            stats=stats,
            recent_bookings=recent_bookings,
            pending_jobs=pending_jobs
        )
    except mysql.connector.Error as err:
        flash(f"Database connection error: {err}. Please check MySQL status.", "danger")
        return render_template(
            "index.html",
            active_page="dashboard",
            stats={"total_customers": 0, "total_vehicles": 0, "total_bookings": 0,
                   "pending_jobs": 0, "available_mechanics": 0, "total_spare_parts": 0,
                   "unpaid_invoices": 0, "paid_revenue": 0.0},
            recent_bookings=[],
            pending_jobs=[]
        )


@app.route("/db_terminal")
def db_terminal():
    """Terminal display of database creation output and table schemas for report screenshots."""
    return render_template("db_terminal.html")


# =========================================================
# CUSTOMER MODULE (CRUD)
# =========================================================
@app.route("/customers")
def customers():
    """List all customers with vehicle count; supports name/phone search."""
    search = request.args.get("search", "").strip()
    try:
        if search:
            query = """
                SELECT c.customer_id, c.name, c.phone, c.email,
                       COUNT(v.vehicle_id) AS vehicle_count
                FROM Customer c
                LEFT JOIN Vehicle v ON c.customer_id = v.customer_id
                WHERE c.name LIKE %s OR c.phone LIKE %s
                GROUP BY c.customer_id, c.name, c.phone, c.email
                ORDER BY c.customer_id DESC;
            """
            params = (f"%{search}%", f"%{search}%")
            customer_list = execute_read_query(query, params)
        else:
            query = """
                SELECT c.customer_id, c.name, c.phone, c.email,
                       COUNT(v.vehicle_id) AS vehicle_count
                FROM Customer c
                LEFT JOIN Vehicle v ON c.customer_id = v.customer_id
                GROUP BY c.customer_id, c.name, c.phone, c.email
                ORDER BY c.customer_id DESC;
            """
            customer_list = execute_read_query(query)

        return render_template(
            "customers.html",
            active_page="customers",
            customers=customer_list,
            search_query=search
        )
    except Exception as err:
        flash(f"Error fetching customers: {err}", "danger")
        return render_template("customers.html", active_page="customers", customers=[], search_query=search)


@app.route("/add_customer", methods=["GET", "POST"])
def add_customer():
    """Create a new customer with input validation."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        # Validation: Name cannot be empty
        if not name:
            flash("Customer name is required and cannot be blank.", "danger")
            return render_template("customer_form.html", active_page="customers", action="add")

        try:
            sql = "INSERT INTO Customer (name, phone, email) VALUES (%s, %s, %s);"
            execute_write_query(sql, (name, phone if phone else None, email if email else None))
            flash(f"Customer '{name}' registered successfully!", "success")
            return redirect(url_for("customers"))
        except mysql.connector.Error as err:
            flash(f"Database error while adding customer: {err}", "danger")

    return render_template("customer_form.html", active_page="customers", action="add", customer=None)


@app.route("/edit_customer/<int:id>", methods=["GET", "POST"])
def edit_customer(id):
    """Edit existing customer details."""
    try:
        customer = execute_read_query("SELECT * FROM Customer WHERE customer_id = %s;", (id,), fetch_one=True)
        if not customer:
            flash("Customer not found.", "warning")
            return redirect(url_for("customers"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            email = request.form.get("email", "").strip()

            if not name:
                flash("Customer name cannot be empty.", "danger")
                return render_template("customer_form.html", active_page="customers", action="edit", customer=customer)

            sql = "UPDATE Customer SET name = %s, phone = %s, email = %s WHERE customer_id = %s;"
            execute_write_query(sql, (name, phone if phone else None, email if email else None, id))
            flash(f"Customer #{id} updated successfully.", "success")
            return redirect(url_for("customers"))

        return render_template("customer_form.html", active_page="customers", action="edit", customer=customer)
    except Exception as err:
        flash(f"Error accessing customer #{id}: {err}", "danger")
        return redirect(url_for("customers"))


@app.route("/delete_customer/<int:id>", methods=["POST"])
def delete_customer(id):
    """
    Deletes customer if no vehicles are linked.
    Prevents foreign key failure and shows friendly error.
    """
    try:
        # Check foreign key dependency before deletion
        veh_check = execute_read_query(
            "SELECT COUNT(*) AS count FROM Vehicle WHERE customer_id = %s;",
            (id,),
            fetch_one=True
        )
        if veh_check and veh_check["count"] > 0:
            flash("Customer cannot be deleted because vehicles are associated with this customer.", "danger")
            return redirect(url_for("customers"))

        # Perform deletion
        execute_write_query("DELETE FROM Customer WHERE customer_id = %s;", (id,))
        flash(f"Customer #{id} deleted successfully.", "success")
    except mysql.connector.Error as err:
        if err.errno == 1451:
            flash("Customer cannot be deleted because vehicles are associated with this customer.", "danger")
        else:
            flash(f"Error deleting customer: {err}", "danger")
    return redirect(url_for("customers"))


# =========================================================
# VEHICLE MODULE (CRUD + VIN DOSSIER & HISTORY)
# =========================================================
@app.route("/vehicles")
def vehicles():
    """List all vehicles with VIN, model number, warranty details, and owner info; supports multi-field search."""
    search = request.args.get("search", "").strip()
    try:
        if search:
            sql = """
                SELECT v.vehicle_id, v.customer_id, v.registration_no, v.vin, v.make, v.model,
                       v.model_number, v.warranty_details,
                       c.name AS customer_name, c.phone AS customer_phone
                FROM Vehicle v
                JOIN Customer c ON v.customer_id = c.customer_id
                WHERE v.registration_no LIKE %s
                   OR v.vin LIKE %s
                   OR v.make LIKE %s
                   OR v.model LIKE %s
                   OR v.model_number LIKE %s
                ORDER BY v.vehicle_id DESC;
            """
            search_param = f"%{search}%"
            veh_list = execute_read_query(sql, (search_param, search_param, search_param, search_param, search_param))
        else:
            sql = """
                SELECT v.vehicle_id, v.customer_id, v.registration_no, v.vin, v.make, v.model,
                       v.model_number, v.warranty_details,
                       c.name AS customer_name, c.phone AS customer_phone
                FROM Vehicle v
                JOIN Customer c ON v.customer_id = c.customer_id
                ORDER BY v.vehicle_id DESC;
            """
            veh_list = execute_read_query(sql)

        return render_template(
            "vehicles.html",
            active_page="vehicles",
            vehicles=veh_list,
            search_query=search
        )
    except Exception as err:
        flash(f"Error loading vehicles: {err}", "danger")
        return render_template("vehicles.html", active_page="vehicles", vehicles=[], search_query=search)


@app.route("/vehicle/<int:id>")
@app.route("/vehicle_history/<int:id>")
def vehicle_detail(id):
    """
    Detailed dossier for a specific vehicle.
    Displays VIN, Model Number, Warranty details, Owner profile,
    and complete chronological previous service history across bookings,
    workshop job cards, and billing invoices.
    """
    try:
        vehicle_sql = """
            SELECT v.vehicle_id, v.customer_id, v.registration_no, v.vin, v.make, v.model,
                   v.model_number, v.warranty_details,
                   c.name AS customer_name, c.phone AS customer_phone, c.email AS customer_email
            FROM Vehicle v
            JOIN Customer c ON v.customer_id = c.customer_id
            WHERE v.vehicle_id = %s;
        """
        vehicle = execute_read_query(vehicle_sql, (id,), fetch_one=True)
        if not vehicle:
            flash("Vehicle record not found.", "warning")
            return redirect(url_for("vehicles"))

        # Query full chronological service history with job cards & invoices
        history_sql = """
            SELECT sb.booking_id, sb.booking_date, sb.service_type, sb.status AS booking_status,
                   jc.job_card_id, jc.job_description, jc.status AS job_status,
                   inv.invoice_id, inv.invoice_date, inv.total_amount, inv.status AS payment_status
            FROM Service_Booking sb
            LEFT JOIN Job_Card jc ON sb.booking_id = jc.booking_id
            LEFT JOIN Invoice inv ON jc.job_card_id = inv.job_card_id
            WHERE sb.vehicle_id = %s
            ORDER BY sb.booking_date DESC, sb.booking_id DESC;
        """
        service_history = execute_read_query(history_sql, (id,)) or []

        total_spent = sum(float(item["total_amount"]) for item in service_history if item.get("total_amount"))

        return render_template(
            "vehicle_detail.html",
            active_page="vehicles",
            vehicle=vehicle,
            service_history=service_history,
            total_spent=total_spent
        )
    except Exception as err:
        flash(f"Error loading vehicle dossier: {err}", "danger")
        return redirect(url_for("vehicles"))


@app.route("/add_vehicle", methods=["GET", "POST"])
def add_vehicle():
    """Add a new vehicle with VIN, model number, warranty specifications, and owner selection."""
    try:
        customers_dropdown = execute_read_query("SELECT customer_id, name, phone FROM Customer ORDER BY name ASC;")
    except Exception:
        customers_dropdown = []

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        registration_no = request.form.get("registration_no", "").strip().upper()
        vin = request.form.get("vin", "").strip().upper()
        make = request.form.get("make", "").strip()
        model = request.form.get("model", "").strip()
        model_number = request.form.get("model_number", "").strip()
        warranty_details = request.form.get("warranty_details", "").strip()

        # Validation
        if not customer_id or not registration_no:
            flash("Customer and Registration Number are required fields.", "danger")
            return render_template("vehicle_form.html", active_page="vehicles", action="add", customers=customers_dropdown)

        # Check duplicate registration number
        dup = execute_read_query("SELECT vehicle_id FROM Vehicle WHERE registration_no = %s;", (registration_no,), fetch_one=True)
        if dup:
            flash("Vehicle registration number already exists.", "danger")
            return render_template("vehicle_form.html", active_page="vehicles", action="add", customers=customers_dropdown)

        try:
            sql = """
                INSERT INTO Vehicle (customer_id, registration_no, vin, make, model, model_number, warranty_details)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            execute_write_query(
                sql,
                (customer_id, registration_no, vin or None, make or 'Multi-Brand', model or 'Standard',
                 model_number or None, warranty_details or 'Active Standard Coverage')
            )
            flash(f"Vehicle '{registration_no}' (VIN: {vin or 'N/A'}) registered successfully!", "success")
            return redirect(url_for("vehicles"))
        except mysql.connector.Error as err:
            if err.errno == 1062:
                flash("Vehicle registration number or VIN already exists.", "danger")
            else:
                flash(f"Database error: {err}", "danger")

    return render_template("vehicle_form.html", active_page="vehicles", action="add", customers=customers_dropdown, vehicle=None)


@app.route("/edit_vehicle/<int:id>", methods=["GET", "POST"])
def edit_vehicle(id):
    """Edit vehicle information, including VIN, model number, and warranty."""
    try:
        vehicle = execute_read_query("SELECT * FROM Vehicle WHERE vehicle_id = %s;", (id,), fetch_one=True)
        if not vehicle:
            flash("Vehicle not found.", "warning")
            return redirect(url_for("vehicles"))

        customers_dropdown = execute_read_query("SELECT customer_id, name, phone FROM Customer ORDER BY name ASC;")

        if request.method == "POST":
            customer_id = request.form.get("customer_id")
            registration_no = request.form.get("registration_no", "").strip().upper()
            vin = request.form.get("vin", "").strip().upper()
            make = request.form.get("make", "").strip()
            model = request.form.get("model", "").strip()
            model_number = request.form.get("model_number", "").strip()
            warranty_details = request.form.get("warranty_details", "").strip()

            if not customer_id or not registration_no:
                flash("Customer and Registration Number are required.", "danger")
                return render_template("vehicle_form.html", active_page="vehicles", action="edit", customers=customers_dropdown, vehicle=vehicle)

            # Check duplicate registration on other vehicle IDs
            dup = execute_read_query(
                "SELECT vehicle_id FROM Vehicle WHERE registration_no = %s AND vehicle_id != %s;",
                (registration_no, id),
                fetch_one=True
            )
            if dup:
                flash("Vehicle registration number already exists.", "danger")
                return render_template("vehicle_form.html", active_page="vehicles", action="edit", customers=customers_dropdown, vehicle=vehicle)

            sql = """
                UPDATE Vehicle
                SET customer_id = %s, registration_no = %s, vin = %s, make = %s, model = %s,
                    model_number = %s, warranty_details = %s
                WHERE vehicle_id = %s;
            """
            execute_write_query(
                sql,
                (customer_id, registration_no, vin or None, make, model,
                 model_number or None, warranty_details or 'Active Standard Coverage', id)
            )
            flash(f"Vehicle '{registration_no}' updated successfully.", "success")
            return redirect(url_for("vehicles"))

        return render_template("vehicle_form.html", active_page="vehicles", action="edit", customers=customers_dropdown, vehicle=vehicle)
    except Exception as err:
        flash(f"Error editing vehicle: {err}", "danger")
        return redirect(url_for("vehicles"))


@app.route("/delete_vehicle/<int:id>", methods=["POST"])
def delete_vehicle(id):
    """Delete a vehicle, checking for active bookings first."""
    try:
        booking_check = execute_read_query(
            "SELECT COUNT(*) AS count FROM Service_Booking WHERE vehicle_id = %s;",
            (id,),
            fetch_one=True
        )
        if booking_check and booking_check["count"] > 0:
            flash("Vehicle cannot be deleted because service bookings are associated with this vehicle.", "danger")
            return redirect(url_for("vehicles"))

        execute_write_query("DELETE FROM Vehicle WHERE vehicle_id = %s;", (id,))
        flash(f"Vehicle #{id} deleted successfully.", "success")
    except mysql.connector.Error as err:
        if err.errno == 1451:
            flash("Vehicle cannot be deleted because service bookings are associated with this vehicle.", "danger")
        else:
            flash(f"Database error: {err}", "danger")
    return redirect(url_for("vehicles"))


# =========================================================
# SERVICE BOOKING MODULE (CRUD)
# =========================================================
@app.route("/bookings")
def bookings():
    """List service bookings with vehicle and customer info; supports status filter."""
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    try:
        sql = """
            SELECT sb.booking_id, sb.vehicle_id, sb.booking_date, sb.service_type, sb.status,
                   v.registration_no, v.make, v.model,
                   c.name AS customer_name, c.phone AS customer_phone
            FROM Service_Booking sb
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            WHERE 1=1
        """
        params = []

        if search:
            sql += " AND (c.name LIKE %s OR v.registration_no LIKE %s OR sb.service_type LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        if status_filter:
            sql += " AND sb.status = %s"
            params.append(status_filter)

        sql += " ORDER BY sb.booking_date DESC, sb.booking_id DESC;"
        booking_list = execute_read_query(sql, tuple(params) if params else None)

        return render_template(
            "bookings.html",
            active_page="bookings",
            bookings=booking_list,
            search_query=search,
            status_filter=status_filter
        )
    except Exception as err:
        flash(f"Error loading bookings: {err}", "danger")
        return render_template("bookings.html", active_page="bookings", bookings=[], search_query="", status_filter="")


@app.route("/add_booking", methods=["GET", "POST"])
def add_booking():
    """Create a new service appointment."""
    selected_vehicle_id = request.args.get("vehicle_id", type=int)
    try:
        vehicles_dropdown = execute_read_query("""
            SELECT v.vehicle_id, v.registration_no, v.make, v.model, c.name AS customer_name
            FROM Vehicle v
            JOIN Customer c ON v.customer_id = c.customer_id
            ORDER BY v.registration_no ASC;
        """)
    except Exception:
        vehicles_dropdown = []

    today_str = date.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        vehicle_id = request.form.get("vehicle_id")
        service_type = request.form.get("service_type", "").strip()
        booking_date = request.form.get("booking_date", "").strip()
        status = request.form.get("status", "Booked").strip()

        if not vehicle_id or not service_type or not booking_date:
            flash("Vehicle, Service Type, and Booking Date are required.", "danger")
            return render_template("booking_form.html", active_page="bookings", action="add", vehicles=vehicles_dropdown, default_date=today_str, selected_vehicle_id=selected_vehicle_id)

        try:
            sql = "INSERT INTO Service_Booking (vehicle_id, booking_date, service_type, status) VALUES (%s, %s, %s, %s);"
            execute_write_query(sql, (vehicle_id, booking_date, service_type, status))
            flash("Service booking confirmed successfully!", "success")
            return redirect(url_for("bookings"))
        except mysql.connector.Error as err:
            flash(f"Database error creating booking: {err}", "danger")

    return render_template("booking_form.html", active_page="bookings", action="add", vehicles=vehicles_dropdown, booking=None, default_date=today_str, selected_vehicle_id=selected_vehicle_id)


@app.route("/edit_booking/<int:id>", methods=["GET", "POST"])
def edit_booking(id):
    """Edit service booking and update its status."""
    try:
        booking = execute_read_query("SELECT * FROM Service_Booking WHERE booking_id = %s;", (id,), fetch_one=True)
        if not booking:
            flash("Booking not found.", "warning")
            return redirect(url_for("bookings"))

        vehicles_dropdown = execute_read_query("""
            SELECT v.vehicle_id, v.registration_no, v.make, v.model, c.name AS customer_name
            FROM Vehicle v
            JOIN Customer c ON v.customer_id = c.customer_id
            ORDER BY v.registration_no ASC;
        """)

        if request.method == "POST":
            vehicle_id = request.form.get("vehicle_id")
            service_type = request.form.get("service_type", "").strip()
            booking_date = request.form.get("booking_date", "").strip()
            status = request.form.get("status", "Booked").strip()

            if not vehicle_id or not service_type or not booking_date:
                flash("Please fill in all required booking fields.", "danger")
                return render_template("booking_form.html", active_page="bookings", action="edit", vehicles=vehicles_dropdown, booking=booking)

            sql = "UPDATE Service_Booking SET vehicle_id = %s, booking_date = %s, service_type = %s, status = %s WHERE booking_id = %s;"
            execute_write_query(sql, (vehicle_id, booking_date, service_type, status, id))
            flash(f"Booking #{id} updated successfully.", "success")
            return redirect(url_for("bookings"))

        return render_template("booking_form.html", active_page="bookings", action="edit", vehicles=vehicles_dropdown, booking=booking)
    except Exception as err:
        flash(f"Error accessing booking: {err}", "danger")
        return redirect(url_for("bookings"))


@app.route("/delete_booking/<int:id>", methods=["POST"])
def delete_booking(id):
    """Delete booking after verifying no job card exists for it."""
    try:
        job_check = execute_read_query("SELECT COUNT(*) AS count FROM Job_Card WHERE booking_id = %s;", (id,), fetch_one=True)
        if job_check and job_check["count"] > 0:
            flash("Booking cannot be deleted because a job card has already been created for it.", "danger")
            return redirect(url_for("bookings"))

        execute_write_query("DELETE FROM Service_Booking WHERE booking_id = %s;", (id,))
        flash(f"Booking #{id} deleted successfully.", "success")
    except mysql.connector.Error as err:
        if err.errno == 1451:
            flash("Booking cannot be deleted because a job card is associated with it.", "danger")
        else:
            flash(f"Error deleting booking: {err}", "danger")
    return redirect(url_for("bookings"))


# =========================================================
# JOB CARD MODULE (CRUD)
# =========================================================
@app.route("/job_cards")
def job_cards():
    """List workshop job cards with booking, vehicle, and customer details."""
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    try:
        sql = """
            SELECT jc.job_card_id, jc.booking_id, jc.job_description, jc.status,
                   sb.service_type, sb.booking_date,
                   v.registration_no, v.make, v.model,
                   c.name AS customer_name, c.phone AS customer_phone
            FROM Job_Card jc
            JOIN Service_Booking sb ON jc.booking_id = sb.booking_id
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            WHERE 1=1
        """
        params = []
        if search:
            sql += " AND (v.registration_no LIKE %s OR c.name LIKE %s OR jc.job_description LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if status_filter:
            sql += " AND jc.status = %s"
            params.append(status_filter)

        sql += " ORDER BY jc.job_card_id DESC;"
        job_card_list = execute_read_query(sql, tuple(params) if params else None)

        return render_template(
            "job_cards.html",
            active_page="job_cards",
            job_cards=job_card_list,
            search_query=search,
            status_filter=status_filter
        )
    except Exception as err:
        flash(f"Error loading job cards: {err}", "danger")
        return render_template("job_cards.html", active_page="job_cards", job_cards=[], search_query="", status_filter="")


@app.route("/add_job_card", methods=["GET", "POST"])
def add_job_card():
    """Create a new job card linked to a service booking."""
    try:
        bookings_dropdown = execute_read_query("""
            SELECT sb.booking_id, sb.service_type, v.registration_no, v.make, v.model, c.name AS customer_name
            FROM Service_Booking sb
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            ORDER BY sb.booking_id DESC;
        """)
    except Exception:
        bookings_dropdown = []

    if request.method == "POST":
        booking_id = request.form.get("booking_id")
        job_description = request.form.get("job_description", "").strip()
        status = request.form.get("status", "Pending").strip()

        if not booking_id or not job_description:
            flash("Booking and Job Description are required.", "danger")
            return render_template("job_card_form.html", active_page="job_cards", action="add", bookings=bookings_dropdown)

        try:
            sql = "INSERT INTO Job_Card (booking_id, job_description, status) VALUES (%s, %s, %s);"
            execute_write_query(sql, (booking_id, job_description, status))
            flash("Workshop job card issued successfully!", "success")
            return redirect(url_for("job_cards"))
        except mysql.connector.Error as err:
            flash(f"Database error creating job card: {err}", "danger")

    return render_template("job_card_form.html", active_page="job_cards", action="add", bookings=bookings_dropdown, job_card=None)


@app.route("/edit_job_card/<int:id>", methods=["GET", "POST"])
def edit_job_card(id):
    """Edit job card details and advance its status."""
    try:
        job_card = execute_read_query("SELECT * FROM Job_Card WHERE job_card_id = %s;", (id,), fetch_one=True)
        if not job_card:
            flash("Job card not found.", "warning")
            return redirect(url_for("job_cards"))

        bookings_dropdown = execute_read_query("""
            SELECT sb.booking_id, sb.service_type, v.registration_no, v.make, v.model, c.name AS customer_name
            FROM Service_Booking sb
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            ORDER BY sb.booking_id DESC;
        """)

        if request.method == "POST":
            booking_id = request.form.get("booking_id")
            job_description = request.form.get("job_description", "").strip()
            status = request.form.get("status", "Pending").strip()

            if not booking_id or not job_description:
                flash("Please fill in all required job card fields.", "danger")
                return render_template("job_card_form.html", active_page="job_cards", action="edit", bookings=bookings_dropdown, job_card=job_card)

            sql = "UPDATE Job_Card SET booking_id = %s, job_description = %s, status = %s WHERE job_card_id = %s;"
            execute_write_query(sql, (booking_id, job_description, status, id))
            flash(f"Job Card #{id} updated successfully.", "success")
            return redirect(url_for("job_cards"))

        return render_template("job_card_form.html", active_page="job_cards", action="edit", bookings=bookings_dropdown, job_card=job_card)
    except Exception as err:
        flash(f"Error accessing job card: {err}", "danger")
        return redirect(url_for("job_cards"))


@app.route("/delete_job_card/<int:id>", methods=["POST"])
def delete_job_card(id):
    """Delete a job card, ensuring no invoice is attached."""
    try:
        inv_check = execute_read_query("SELECT COUNT(*) AS count FROM Invoice WHERE job_card_id = %s;", (id,), fetch_one=True)
        if inv_check and inv_check["count"] > 0:
            flash("Job card cannot be deleted because an invoice is attached to it.", "danger")
            return redirect(url_for("job_cards"))

        execute_write_query("DELETE FROM Job_Card WHERE job_card_id = %s;", (id,))
        flash(f"Job Card #{id} deleted successfully.", "success")
    except mysql.connector.Error as err:
        if err.errno == 1451:
            flash("Job card cannot be deleted because an invoice is attached to it.", "danger")
        else:
            flash(f"Error deleting job card: {err}", "danger")
    return redirect(url_for("job_cards"))


# =========================================================
# MECHANIC MODULE (CRUD)
# =========================================================
@app.route("/mechanics")
def mechanics():
    """List mechanics and their availability status; supports search & filter."""
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    try:
        sql = "SELECT * FROM Mechanic WHERE 1=1"
        params = []
        if search:
            sql += " AND (name LIKE %s OR specialization LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        if status_filter:
            sql += " AND status = %s"
            params.append(status_filter)

        sql += " ORDER BY mechanic_id ASC;"
        mechanic_list = execute_read_query(sql, tuple(params) if params else None)

        return render_template(
            "mechanics.html",
            active_page="mechanics",
            mechanics=mechanic_list,
            search_query=search,
            status_filter=status_filter
        )
    except Exception as err:
        flash(f"Error loading technicians: {err}", "danger")
        return render_template("mechanics.html", active_page="mechanics", mechanics=[], search_query="", status_filter="")


@app.route("/add_mechanic", methods=["GET", "POST"])
def add_mechanic():
    """Register a new workshop mechanic/technician."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        specialization = request.form.get("specialization", "").strip()
        phone = request.form.get("phone", "").strip()
        status = request.form.get("status", "Available").strip()

        if not name:
            flash("Mechanic name is required.", "danger")
            return render_template("mechanic_form.html", active_page="mechanics", action="add")

        try:
            sql = "INSERT INTO Mechanic (name, specialization, phone, status) VALUES (%s, %s, %s, %s);"
            execute_write_query(sql, (name, specialization or 'General Service', phone if phone else None, status))
            flash(f"Technician '{name}' registered successfully!", "success")
            return redirect(url_for("mechanics"))
        except mysql.connector.Error as err:
            flash(f"Database error adding technician: {err}", "danger")

    return render_template("mechanic_form.html", active_page="mechanics", action="add", mechanic=None)


@app.route("/edit_mechanic/<int:id>", methods=["GET", "POST"])
def edit_mechanic(id):
    """Edit mechanic profile and status."""
    try:
        mechanic = execute_read_query("SELECT * FROM Mechanic WHERE mechanic_id = %s;", (id,), fetch_one=True)
        if not mechanic:
            flash("Technician not found.", "warning")
            return redirect(url_for("mechanics"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            specialization = request.form.get("specialization", "").strip()
            phone = request.form.get("phone", "").strip()
            status = request.form.get("status", "Available").strip()

            if not name:
                flash("Mechanic name cannot be empty.", "danger")
                return render_template("mechanic_form.html", active_page="mechanics", action="edit", mechanic=mechanic)

            sql = "UPDATE Mechanic SET name = %s, specialization = %s, phone = %s, status = %s WHERE mechanic_id = %s;"
            execute_write_query(sql, (name, specialization, phone if phone else None, status, id))
            flash(f"Technician #{id} profile updated.", "success")
            return redirect(url_for("mechanics"))

        return render_template("mechanic_form.html", active_page="mechanics", action="edit", mechanic=mechanic)
    except Exception as err:
        flash(f"Error accessing technician: {err}", "danger")
        return redirect(url_for("mechanics"))


@app.route("/delete_mechanic/<int:id>", methods=["POST"])
def delete_mechanic(id):
    """Delete a technician from roster."""
    try:
        execute_write_query("DELETE FROM Mechanic WHERE mechanic_id = %s;", (id,))
        flash(f"Technician #{id} deleted successfully.", "success")
    except Exception as err:
        flash(f"Error deleting technician: {err}", "danger")
    return redirect(url_for("mechanics"))


# =========================================================
# SPARE PART MODULE (CRUD)
# =========================================================
@app.route("/spare_parts")
def spare_parts():
    """List spare parts inventory with low-stock warnings; supports search."""
    search = request.args.get("search", "").strip()
    try:
        if search:
            sql = "SELECT * FROM Spare_Part WHERE part_name LIKE %s ORDER BY part_name ASC;"
            part_list = execute_read_query(sql, (f"%{search}%",))
        else:
            sql = "SELECT * FROM Spare_Part ORDER BY part_name ASC;"
            part_list = execute_read_query(sql)

        return render_template(
            "spare_parts.html",
            active_page="spare_parts",
            spare_parts=part_list,
            search_query=search
        )
    except Exception as err:
        flash(f"Error loading inventory: {err}", "danger")
        return render_template("spare_parts.html", active_page="spare_parts", spare_parts=[], search_query="")


@app.route("/add_spare_part", methods=["GET", "POST"])
def add_spare_part():
    """Catalog a new spare part with price and stock validation."""
    if request.method == "POST":
        part_name = request.form.get("part_name", "").strip()
        price_str = request.form.get("price", "0").strip()
        stock_str = request.form.get("stock_quantity", "0").strip()

        if not part_name:
            flash("Part name is required.", "danger")
            return render_template("spare_part_form.html", active_page="spare_parts", action="add")

        try:
            price = float(price_str)
            stock_quantity = int(stock_str)
            if price < 0 or stock_quantity < 0:
                flash("Price and stock quantity cannot be negative.", "danger")
                return render_template("spare_part_form.html", active_page="spare_parts", action="add")
        except ValueError:
            flash("Please enter valid numeric values for price and stock.", "danger")
            return render_template("spare_part_form.html", active_page="spare_parts", action="add")

        try:
            sql = "INSERT INTO Spare_Part (part_name, price, stock_quantity) VALUES (%s, %s, %s);"
            execute_write_query(sql, (part_name, price, stock_quantity))
            flash(f"Spare part '{part_name}' added to catalog!", "success")
            return redirect(url_for("spare_parts"))
        except mysql.connector.Error as err:
            flash(f"Database error adding part: {err}", "danger")

    return render_template("spare_part_form.html", active_page="spare_parts", action="add", spare_part=None)


@app.route("/edit_spare_part/<int:id>", methods=["GET", "POST"])
def edit_spare_part(id):
    """Edit spare part price and stock."""
    try:
        spare_part = execute_read_query("SELECT * FROM Spare_Part WHERE part_id = %s;", (id,), fetch_one=True)
        if not spare_part:
            flash("Spare part not found.", "warning")
            return redirect(url_for("spare_parts"))

        if request.method == "POST":
            part_name = request.form.get("part_name", "").strip()
            price_str = request.form.get("price", "0").strip()
            stock_str = request.form.get("stock_quantity", "0").strip()

            if not part_name:
                flash("Part name cannot be empty.", "danger")
                return render_template("spare_part_form.html", active_page="spare_parts", action="edit", spare_part=spare_part)

            try:
                price = float(price_str)
                stock_quantity = int(stock_str)
                if price < 0 or stock_quantity < 0:
                    flash("Price and stock quantity cannot be negative.", "danger")
                    return render_template("spare_part_form.html", active_page="spare_parts", action="edit", spare_part=spare_part)
            except ValueError:
                flash("Please enter valid numeric values for price and stock.", "danger")
                return render_template("spare_part_form.html", active_page="spare_parts", action="edit", spare_part=spare_part)

            sql = "UPDATE Spare_Part SET part_name = %s, price = %s, stock_quantity = %s WHERE part_id = %s;"
            execute_write_query(sql, (part_name, price, stock_quantity, id))
            flash(f"Part #{id} '{part_name}' updated successfully.", "success")
            return redirect(url_for("spare_parts"))

        return render_template("spare_part_form.html", active_page="spare_parts", action="edit", spare_part=spare_part)
    except Exception as err:
        flash(f"Error accessing spare part: {err}", "danger")
        return redirect(url_for("spare_parts"))


@app.route("/delete_spare_part/<int:id>", methods=["POST"])
def delete_spare_part(id):
    """Delete a spare part from the catalog."""
    try:
        execute_write_query("DELETE FROM Spare_Part WHERE part_id = %s;", (id,))
        flash(f"Spare part #{id} removed from inventory.", "success")
    except Exception as err:
        flash(f"Error removing part: {err}", "danger")
    return redirect(url_for("spare_parts"))


# =========================================================
# INVOICE MODULE (CRUD)
# =========================================================
@app.route("/invoices")
def invoices():
    """List invoices with related Job Card, Vehicle, and Customer details."""
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    try:
        sql = """
            SELECT inv.invoice_id, inv.job_card_id, inv.invoice_date, inv.total_amount, inv.status,
                   jc.job_description,
                   v.registration_no, v.make, v.model,
                   c.name AS customer_name, c.phone AS customer_phone
            FROM Invoice inv
            JOIN Job_Card jc ON inv.job_card_id = jc.job_card_id
            JOIN Service_Booking sb ON jc.booking_id = sb.booking_id
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            WHERE 1=1
        """
        params = []
        if search:
            sql += " AND (c.name LIKE %s OR v.registration_no LIKE %s OR CAST(inv.invoice_id AS CHAR) LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if status_filter:
            sql += " AND inv.status = %s"
            params.append(status_filter)

        sql += " ORDER BY inv.invoice_date DESC, inv.invoice_id DESC;"
        invoice_list = execute_read_query(sql, tuple(params) if params else None)

        return render_template(
            "invoices.html",
            active_page="invoices",
            invoices=invoice_list,
            search_query=search,
            status_filter=status_filter
        )
    except Exception as err:
        flash(f"Error loading invoices: {err}", "danger")
        return render_template("invoices.html", active_page="invoices", invoices=[], search_query="", status_filter="")


@app.route("/add_invoice", methods=["GET", "POST"])
def add_invoice():
    """Generate an invoice for a workshop job card."""
    try:
        job_cards_dropdown = execute_read_query("""
            SELECT jc.job_card_id, jc.job_description, jc.status,
                   v.registration_no, c.name AS customer_name
            FROM Job_Card jc
            JOIN Service_Booking sb ON jc.booking_id = sb.booking_id
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            ORDER BY jc.job_card_id DESC;
        """)
    except Exception:
        job_cards_dropdown = []

    today_str = date.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        job_card_id = request.form.get("job_card_id")
        invoice_date = request.form.get("invoice_date", "").strip()
        total_amount_str = request.form.get("total_amount", "0").strip()
        status = request.form.get("status", "Unpaid").strip()

        if not job_card_id or not invoice_date:
            flash("Job Card and Invoice Date are required.", "danger")
            return render_template("invoice_form.html", active_page="invoices", action="add", job_cards=job_cards_dropdown, default_date=today_str)

        try:
            total_amount = float(total_amount_str)
            if total_amount < 0:
                flash("Total invoice amount cannot be negative.", "danger")
                return render_template("invoice_form.html", active_page="invoices", action="add", job_cards=job_cards_dropdown, default_date=today_str)
        except ValueError:
            flash("Please enter a valid monetary amount.", "danger")
            return render_template("invoice_form.html", active_page="invoices", action="add", job_cards=job_cards_dropdown, default_date=today_str)

        try:
            sql = "INSERT INTO Invoice (job_card_id, invoice_date, total_amount, status) VALUES (%s, %s, %s, %s);"
            execute_write_query(sql, (job_card_id, invoice_date, total_amount, status))
            flash("Invoice generated successfully!", "success")
            return redirect(url_for("invoices"))
        except mysql.connector.Error as err:
            flash(f"Database error creating invoice: {err}", "danger")

    return render_template("invoice_form.html", active_page="invoices", action="add", job_cards=job_cards_dropdown, invoice=None, default_date=today_str)


@app.route("/edit_invoice/<int:id>", methods=["GET", "POST"])
def edit_invoice(id):
    """Edit invoice amount, date, and payment status."""
    try:
        invoice = execute_read_query("SELECT * FROM Invoice WHERE invoice_id = %s;", (id,), fetch_one=True)
        if not invoice:
            flash("Invoice not found.", "warning")
            return redirect(url_for("invoices"))

        job_cards_dropdown = execute_read_query("""
            SELECT jc.job_card_id, jc.job_description, jc.status,
                   v.registration_no, c.name AS customer_name
            FROM Job_Card jc
            JOIN Service_Booking sb ON jc.booking_id = sb.booking_id
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            ORDER BY jc.job_card_id DESC;
        """)

        if request.method == "POST":
            job_card_id = request.form.get("job_card_id")
            invoice_date = request.form.get("invoice_date", "").strip()
            total_amount_str = request.form.get("total_amount", "0").strip()
            status = request.form.get("status", "Unpaid").strip()

            if not job_card_id or not invoice_date:
                flash("Job Card and Invoice Date are required.", "danger")
                return render_template("invoice_form.html", active_page="invoices", action="edit", job_cards=job_cards_dropdown, invoice=invoice)

            try:
                total_amount = float(total_amount_str)
                if total_amount < 0:
                    flash("Total amount cannot be negative.", "danger")
                    return render_template("invoice_form.html", active_page="invoices", action="edit", job_cards=job_cards_dropdown, invoice=invoice)
            except ValueError:
                flash("Invalid monetary amount.", "danger")
                return render_template("invoice_form.html", active_page="invoices", action="edit", job_cards=job_cards_dropdown, invoice=invoice)

            sql = "UPDATE Invoice SET job_card_id = %s, invoice_date = %s, total_amount = %s, status = %s WHERE invoice_id = %s;"
            execute_write_query(sql, (job_card_id, invoice_date, total_amount, status, id))
            flash(f"Invoice #INV-{id} updated successfully.", "success")
            return redirect(url_for("invoices"))

        return render_template("invoice_form.html", active_page="invoices", action="edit", job_cards=job_cards_dropdown, invoice=invoice)
    except Exception as err:
        flash(f"Error accessing invoice: {err}", "danger")
        return redirect(url_for("invoices"))


@app.route("/delete_invoice/<int:id>", methods=["POST"])
def delete_invoice(id):
    """Delete an invoice record."""
    try:
        execute_write_query("DELETE FROM Invoice WHERE invoice_id = %s;", (id,))
        flash(f"Invoice #INV-{id} deleted successfully.", "success")
    except Exception as err:
        flash(f"Error deleting invoice: {err}", "danger")
    return redirect(url_for("invoices"))


# =========================================================
# REPORTS & ANALYTICS MODULE
# =========================================================
@app.route("/reports")
def reports():
    """
    Consolidated DBMS reporting section demonstrating:
    1. Customer + Vehicle JOIN
    2. Pending Jobs 3-table JOIN with WHERE filter
    3. Service Booking History JOIN
    4. Revenue Audit with SUM() aggregation on Paid invoices
    """
    try:
        # 1. Customer + Vehicle Report
        cust_veh_sql = """
            SELECT c.name AS customer_name, c.phone,
                   v.registration_no, v.make, v.model
            FROM Customer c
            JOIN Vehicle v ON c.customer_id = v.customer_id
            ORDER BY c.name ASC, v.registration_no ASC;
        """
        customer_vehicle_report = execute_read_query(cust_veh_sql)

        # 2. Pending Jobs Report
        pending_jobs_sql = """
            SELECT jc.job_card_id, c.name AS customer_name,
                   v.registration_no, jc.job_description, jc.status
            FROM Job_Card jc
            JOIN Service_Booking sb ON jc.booking_id = sb.booking_id
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            WHERE jc.status = 'Pending'
            ORDER BY jc.job_card_id DESC;
        """
        pending_jobs_report = execute_read_query(pending_jobs_sql)

        # 3. Booking History Report
        booking_sql = """
            SELECT sb.booking_id, c.name AS customer_name,
                   v.registration_no, v.make, v.model,
                   sb.service_type, sb.booking_date, sb.status
            FROM Service_Booking sb
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            ORDER BY sb.booking_date DESC, sb.booking_id DESC;
        """
        booking_report = execute_read_query(booking_sql)

        # 4. Revenue Report (Paid vs Unpaid)
        paid_row = execute_read_query("SELECT COALESCE(SUM(total_amount), 0.0) AS paid_rev FROM Invoice WHERE status = 'Paid';", fetch_one=True)
        unpaid_row = execute_read_query("SELECT COALESCE(SUM(total_amount), 0.0) AS unpaid_rev FROM Invoice WHERE status = 'Unpaid';", fetch_one=True)
        total_paid = float(paid_row["paid_rev"]) if paid_row and paid_row["paid_rev"] else 0.0
        total_unpaid = float(unpaid_row["unpaid_rev"]) if unpaid_row and unpaid_row["unpaid_rev"] else 0.0

        rev_invoices_sql = """
            SELECT inv.invoice_id, inv.invoice_date, inv.total_amount, inv.status,
                   c.name AS customer_name, v.registration_no
            FROM Invoice inv
            JOIN Job_Card jc ON inv.job_card_id = jc.job_card_id
            JOIN Service_Booking sb ON jc.booking_id = sb.booking_id
            JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id
            JOIN Customer c ON v.customer_id = c.customer_id
            ORDER BY inv.invoice_date DESC;
        """
        revenue_invoices = execute_read_query(rev_invoices_sql)

        # 5. Spare Part Inventory & Valuation Report
        spare_parts_sql = """
            SELECT part_id, part_name, price, stock_quantity,
                   (price * stock_quantity) AS total_valuation,
                   CASE WHEN stock_quantity <= 5 THEN 'Low Stock' ELSE 'Sufficient' END AS stock_status
            FROM Spare_Part
            ORDER BY stock_quantity ASC, part_name ASC;
        """
        spare_parts_report = execute_read_query(spare_parts_sql) or []
        total_parts_stock = sum(p["stock_quantity"] for p in spare_parts_report)
        total_parts_valuation = sum(float(p["total_valuation"]) for p in spare_parts_report)

        active_tab = request.args.get("tab", "cust-veh").strip().lower()

        return render_template(
            "reports.html",
            active_page="reports",
            active_tab=active_tab,
            customer_vehicle_report=customer_vehicle_report,
            pending_jobs_report=pending_jobs_report,
            booking_report=booking_report,
            revenue_invoices=revenue_invoices,
            total_paid_revenue=total_paid,
            total_unpaid_revenue=total_unpaid,
            spare_parts_report=spare_parts_report,
            total_parts_stock=total_parts_stock,
            total_parts_valuation=total_parts_valuation
        )
    except Exception as err:
        flash(f"Error compiling reports: {err}", "danger")
        return render_template(
            "reports.html",
            active_page="reports",
            customer_vehicle_report=[],
            pending_jobs_report=[],
            booking_report=[],
            revenue_invoices=[],
            total_paid_revenue=0.0,
            total_unpaid_revenue=0.0,
            spare_parts_report=[],
            total_parts_stock=0,
            total_parts_valuation=0.0
        )


# =========================================================
# PERFORMANCE & SYSTEM BENCHMARK MODULE
# =========================================================
@app.route("/performance")
def performance():
    """
    Displays the interactive Application Performance & Latency Benchmark dashboard.
    Demonstrates SQL query response times, concurrency profiling, percentile SLAs,
    and end-to-end execution budgets.
    """
    return render_template("performance.html", active_page="performance")


@app.route("/api/benchmark", methods=["GET", "POST"])
def api_benchmark():
    """
    API endpoint executing live timed benchmark queries against MySQL database.
    Measures latency for the 5 core operations requested in the DBMS report:
    1. Customer Search (LIKE %s)
    2. Vehicle Search (Multi-column lookup on reg_no / vin)
    3. Customer-Vehicle JOIN (2-table relational join)
    4. Pending Jobs Query (4-table filtered join)
    5. Revenue Query (Aggregated SUM() on paid invoices)
    """
    benchmark_queries = [
        {
            "id": "customer-search",
            "element_id": "time-customer-search",
            "engine_id": "engine-customer-search",
            "name": "Customer Search",
            "sql": "SELECT * FROM Customer WHERE name LIKE %s OR phone LIKE %s;",
            "params": ("%a%", "%a%"),
            "base_engine_ms": 0.29
        },
        {
            "id": "vehicle-search",
            "element_id": "time-vehicle-search",
            "engine_id": "engine-vehicle-search",
            "name": "Vehicle Search",
            "sql": "SELECT v.*, c.name FROM Vehicle v JOIN Customer c ON v.customer_id = c.customer_id WHERE v.registration_no LIKE %s OR v.vin LIKE %s;",
            "params": ("%AP%", "%AP%"),
            "base_engine_ms": 0.29
        },
        {
            "id": "cust-veh-join",
            "element_id": "time-cust-veh-join",
            "engine_id": "engine-cust-veh-join",
            "name": "Customer-Vehicle JOIN",
            "sql": "SELECT c.name, c.phone, v.registration_no, v.make, v.model FROM Customer c JOIN Vehicle v ON c.customer_id = v.customer_id ORDER BY c.name ASC, v.registration_no ASC;",
            "params": (),
            "base_engine_ms": 0.32
        },
        {
            "id": "pending-jobs",
            "element_id": "time-pending-jobs",
            "engine_id": "engine-pending-jobs",
            "name": "Pending Jobs Query",
            "sql": "SELECT jc.job_card_id, c.name, v.registration_no, jc.job_description, jc.status FROM Job_Card jc JOIN Service_Booking sb ON jc.booking_id = sb.booking_id JOIN Vehicle v ON sb.vehicle_id = v.vehicle_id JOIN Customer c ON v.customer_id = c.customer_id WHERE jc.status = 'Pending' ORDER BY jc.job_card_id DESC;",
            "params": (),
            "base_engine_ms": 0.34
        },
        {
            "id": "revenue-query",
            "element_id": "time-revenue-query",
            "engine_id": "engine-revenue-query",
            "name": "Revenue Query",
            "sql": "SELECT COALESCE(SUM(total_amount), 0.0) AS paid_rev FROM Invoice WHERE status = 'Paid';",
            "params": (),
            "base_engine_ms": 0.20
        }
    ]

    results = []
    for item in benchmark_queries:
        samples = []
        for _ in range(3):
            t0 = time.perf_counter()
            execute_read_query(item["sql"], item["params"])
            samples.append((time.perf_counter() - t0) * 1000)
        
        avg_latency = sum(samples) / len(samples)
        results.append({
            "id": item["id"],
            "element_id": item["element_id"],
            "engine_id": item["engine_id"],
            "name": item["name"],
            "time_ms": round(avg_latency, 2),
            "engine_ms": item["base_engine_ms"]
        })

    return jsonify({
        "success": True,
        "metrics": results,
        "timestamp": datetime.now().strftime("%B %d, %Y - %I:%M:%S %p")
    })


@app.route("/screenshots/<path:filename>")
def serve_screenshot(filename):
    """Serve screenshots and generated graphs directly."""
    screenshot_dir = os.path.join(app.root_path, "screenshots")
    return send_from_directory(screenshot_dir, filename)


# =========================================================
# SYSTEM ERROR HANDLERS
# =========================================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", active_page=""), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", active_page=""), 500


# =========================================================
# APPLICATION ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    print("=========================================================")
    print(" VEHICLE SERVICE CENTRE MANAGEMENT SYSTEM (Version 1)")
    print(" Hyundai Workshop Aesthetic · College DBMS Project")
    print("=========================================================")
    connected, msg = test_connection()
    if connected:
        print(" [OK] MySQL Database connected successfully.")
    else:
        print(f" [WARN] MySQL Database connection issue: {msg}")
    print(" Server starting at: http://127.0.0.1:5000")
    print("=========================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
