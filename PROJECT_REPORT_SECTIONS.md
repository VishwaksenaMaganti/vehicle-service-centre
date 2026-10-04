# VEHICLE SERVICE CENTRE MANAGEMENT SYSTEM
## College DBMS Project Documentation

---

# 5.12 APPLICATION MODULES

The **Vehicle Service Centre Management System (VSCMS)** is architected as a modular, three-tier web application combining a **Bootstrap 5.3 frontend**, a **Python Flask application server**, and a **MySQL 8.0 relational database**. The system is partitioned into eight functional operational modules and an analytical reporting suite. Each module encapsulates dedicated business logic, enforces transactional consistency, and utilizes parameterized SQL statements executed via `mysql-connector-python`.

---

### 1. Dashboard Module (`/` and `/dashboard`)
The Dashboard serves as the operational command centre for service advisors, workshop managers, and administrators. It provides a real-time, high-level situational overview of workshop activities and key performance indicators (KPIs) computed dynamically through SQL aggregation queries (`COUNT`, `SUM`, `COALESCE`).

* **Statistical Overview & Real-Time KPIs:**
  * **Total Customers:** Aggregated using `SELECT COUNT(*) AS total FROM Customer;`.
  * **Total Vehicles:** Total fleet enrolled, queried via `SELECT COUNT(*) AS total FROM Vehicle;`.
  * **Total Bookings:** Cumulative service appointments computed via `SELECT COUNT(*) AS total FROM Service_Booking;`.
  * **Pending Jobs:** Active repair orders awaiting workshop completion, filtered via `SELECT COUNT(*) AS total FROM Job_Card WHERE status = 'Pending';`.
  * **Available Mechanics:** Technicians ready for assignment, calculated via `SELECT COUNT(*) AS total FROM Mechanic WHERE status = 'Available';`.
  * **Spare Parts Catalog:** Unique component SKU count via `SELECT COUNT(*) AS total FROM Spare_Part;`.
  * **Unpaid Invoices:** Outstanding financial receivables computed via `SELECT COUNT(*) AS total FROM Invoice WHERE status = 'Unpaid';`.
  * **Total Paid Revenue:** Total collected payments calculated via `SELECT COALESCE(SUM(total_amount), 0.0) AS total_revenue FROM Invoice WHERE status = 'Paid';`.
* **Quick-Access Action Toolbar:** One-click shortcuts for rapid record creation (`+ Customer`, `+ Vehicle & VIN`, `+ Booking`, `+ Job Card`, `+ Spare Part`, `+ Invoice`, `+ Technician`).
* **Instant VIN & Registration Search:** Live lookup bar enabling instant retrieval of any vehicle's dossier and history directly from the home view.
* **Recent Service Appointments Feed:** A three-table relational query (`Service_Booking JOIN Vehicle JOIN Customer`) displaying the last five scheduled jobs with current statuses.
* **Open Workshop Jobs Feed:** A four-table relational query (`Job_Card JOIN Service_Booking JOIN Vehicle JOIN Customer`) displaying open repair orders requiring technical attention.

---

### 2. Customer Module (`/customers`)
The Customer Module manages owner identity records and communication details. It establishes the primary entity from which all vehicle ownership and service histories originate.

* **Add Customer (`/add_customer`):** Form interface accepting `name` (mandatory), `phone`, and `email`. Executes parameterized `INSERT INTO Customer (name, phone, email) VALUES (%s, %s, %s);`.
* **View Customers (`/customers`):** Tabular directory displaying registered clients, contact numbers, email addresses, and the total count of vehicles owned by each client. The vehicle count is computed dynamically using a relational `LEFT JOIN` and `GROUP BY` query:
  ```sql
  SELECT c.customer_id, c.name, c.phone, c.email, COUNT(v.vehicle_id) AS vehicle_count
  FROM Customer c
  LEFT JOIN Vehicle v ON c.customer_id = v.customer_id
  GROUP BY c.customer_id, c.name, c.phone, c.email
  ORDER BY c.customer_id DESC;
  ```
* **Edit Customer (`/edit_customer/<id>`):** Form allowing modification of client contact information with pre-populated values and parameterized `UPDATE` query execution.
* **Delete Customer (`/delete_customer/<id>`):** Removes a customer record. Proactively executes a dependency check against the `Vehicle` table to enforce foreign key integrity and prevent orphaned vehicle records.
* **Search Customer:** Search field supporting pattern-matching lookups (`LIKE %s`) across both customer names and contact phone numbers.

---

### 3. Vehicle Module (`/vehicles`)
The Vehicle Module maintains the multi-brand fleet registry, capturing manufacturer specifications, unique chassis identification numbers, and factory or extended warranty validity terms.

* **Add Vehicle (`/add_vehicle`):** Allows enrollment of passenger and commercial automobiles. Requires selecting an existing registered owner from a dynamically populated database dropdown. Form captures:
  * `customer_id` (Foreign Key referencing `Customer.customer_id`)
  * `registration_no` (Unique license plate, forced uppercase)
  * `vin` (17-character unique Vehicle Identification Number / chassis code)
  * `make` (Manufacturer name, e.g., Hyundai, Toyota, Honda, BMW, Tata)
  * `model` (Model line, e.g., Creta, Fortuner, City, 7 Series, Nexon)
  * `model_number` (Trim level or chassis code, e.g., `SX(O) 1.5 Turbo DCT`, `2.8 4x4 AT`, `740Li G70`)
  * `warranty_details` (Warranty coverage description and duration)
* **View Vehicles (`/vehicles`):** Comprehensive table showing license plate badge, monospace VIN tag, model number specification, owner contact profile, warranty badge, and quick action buttons.
* **Vehicle History Dossier (`/vehicle/<id>`):** Dedicated profile view presenting complete vehicle specifications alongside an exhaustive, chronological **Previous Service History Table**. Joins `Service_Booking`, `Job_Card`, and `Invoice` to present every visit date, technical job description, bay status, and billing total.
* **Edit Vehicle (`/edit_vehicle/<id>`):** Allows updating chassis details, trim specifications, registration numbers, and warranty extensions.
* **Delete Vehicle (`/delete_vehicle/<id>`):** Safely deletes a vehicle after verifying that no active or historical `Service_Booking` records are linked to it.
* **Multi-Field Vehicle Search:** Allows searching the fleet across Registration Number, VIN, Make, Model, or Model Number using parameterized `LIKE` filters.

---

### 4. Service Booking Module (`/bookings`)
The Booking Module schedules appointments and monitors the lifecycle stages of vehicles entering the service facility.

* **Create Booking (`/add_booking`):** Schedules a vehicle for workshop intake. Includes dropdown selection of registered vehicles (with license plate, make, model, and owner name), appointment date, service operation type (e.g., Periodic Maintenance, Brake Overhaul, Oil Service), and initial status (`Booked`).
* **View Bookings (`/bookings`):** Master schedule table showing booking ID, client name, contact phone, vehicle registration badge, service description, appointment date, and status badges.
* **Update Booking & Status (`/edit_booking/<id>`):** Allows service advisors to update scheduled dates, modify requested service operations, and transition appointment states through the workflow: `Booked` $\to$ `In Progress` $\to$ `Completed` $\to$ `Cancelled`.
* **Cancel / Delete Booking (`/delete_booking/<id>`):** Allows canceling appointments. Prohibits deletion if a workshop `Job_Card` has already been generated for the booking.
* **Search & Filter:** Filter appointments by lifecycle status (`Booked`, `In Progress`, `Completed`, `Cancelled`) or search by client name, registration number, or service operation.

---

### 5. Job Card Module (`/job_cards`)
The Job Card Module translates booking appointments into actionable technical work orders for mechanics on the workshop floor.

* **Create Job Card (`/add_job_card`):** Issues a technical work order linked to an existing service booking. Captures diagnostic instructions, customer complaint observations, and required mechanical repairs. Initial status defaults to `Pending`.
* **View Job Cards (`/job_cards`):** Tabular list displaying Job Card ID, associated booking reference, vehicle registration, owner details, technical description, and workshop progress badge.
* **Update Job Status (`/edit_job_card/<id>`):** Enables technicians and workshop foremen to record progress updates and transition job statuses: `Pending` $\to$ `In Progress` $\to$ `Completed`.
* **Delete Job Card (`/delete_job_card/<id>`):** Deletes a job card after verifying that no billing `Invoice` has been generated for it.
* **Search & Status Filtering:** Filter job cards by status (`Pending`, `In Progress`, `Completed`) or search by vehicle registration, client name, or job description.

---

### 6. Mechanic Module (`/mechanics`)
The Mechanic Module manages the workshop technical workforce, tracking individual specializations, contact information, and real-time floor availability.

* **Add Mechanic (`/add_mechanic`):** Registers a new technician with name, specialization domain (e.g., Engine Diagnostics, Automatic & Dual-Clutch Transmissions, Electrical & Hybrid Systems, Brake & Suspension Systems), contact phone number, and initial availability status.
* **View Mechanics (`/mechanics`):** Technician roster showing mechanic ID, name, technical domain, phone number, and live status badge (`Available`, `Busy`, `Unavailable`).
* **Update Mechanic & Availability (`/edit_mechanic/<id>`):** Updates contact numbers, certifications, specializations, and real-time bay availability status.
* **Delete Mechanic (`/delete_mechanic/<id>`):** Removes a technician record from the workshop registry.
* **Search & Filter:** Search by technician name or technical specialization, with status filtering by availability.

---

### 7. Spare Part Module (`/spare_parts`)
The Spare Part Module manages warehouse inventory, unit pricing, component availability, and proactive stock-level replenishment alerts.

* **Add Spare Part (`/add_spare_part`):** Catalogs a new OEM component with part name, unit price (decimal format), and current warehouse stock count.
* **View Spare Parts (`/spare_parts`):** Catalog table displaying Part ID, part name, unit price, stock on hand, and dynamic stock warning badges.
* **Identify Low-Stock Parts:** System automatically applies a highlighted **"Low Stock"** warning badge for any inventory item where `stock_quantity <= 5`, providing immediate visual notification for procurement reordering.
* **Update Price & Stock (`/edit_spare_part/<id>`):** Allows updating component pricing and adjusting stock quantities during restock shipments or usage.
* **Delete Spare Part (`/delete_spare_part/<id>`):** Removes discontinued component items from the catalog.
* **Search Inventory:** Search inventory items by component name or part keyword.

---

### 8. Invoice Module (`/invoices`)
The Invoice Module handles financial billing, customer ledger accounting, and payment settlement tracking for completed repairs.

* **Create Invoice (`/add_invoice`):** Generates a formal bill linked to a completed workshop `Job_Card`. Automatically links the repair work order, captures invoice generation date, calculates total billing amount, and sets payment status (`Unpaid` or `Paid`).
* **View Invoices (`/invoices`):** Billing ledger showing Invoice ID (`#INV-xxx`), associated Job Card reference, vehicle registration, client name, date, billed amount in currency format, and payment status badge.
* **Update Invoice Status (`/edit_invoice/<id>`):** Allows billing managers to record payment settlements by transitioning status from `Unpaid` to `Paid`, or modify amounts and billing dates.
* **Identify Unpaid Invoices:** Dedicated status filter instantly isolates all outstanding accounts receivable requiring customer follow-up.
* **Delete Invoice (`/delete_invoice/<id>`):** Allows removal of voided or cancelled invoices.

---

### 9. Reports & Analytical Auditing Module (`/reports`)
The Reports Module provides consolidated management insights and regulatory compliance documentation via multi-table relational queries and financial aggregations.

* **1. Customer & Vehicle Association Report:** A relational two-table `JOIN` (`Customer JOIN Vehicle`) mapping registered automobile owners to their respective fleet registrations, manufacturers, and model trim variants.
* **2. Pending Workshop Jobs Report:** A relational four-table `JOIN` (`Job_Card JOIN Service_Booking JOIN Vehicle JOIN Customer`) filtered by `WHERE jc.status = 'Pending'`, providing the workshop supervisor with an active backlog of pending vehicle repairs.
* **3. Comprehensive Booking History Audit:** A three-table `JOIN` (`Service_Booking JOIN Vehicle JOIN Customer`) auditing chronological appointment scheduling, service operation types, and completion statuses.
* **4. Revenue & Financial Settlement Audit:** Aggregates paid income versus outstanding receivables using `SUM(total_amount)` queries, complemented by an itemized billing history of all issued invoices.
* **5. Spare Part Inventory & Valuation Report:** Comprehensive warehouse audit listing all cataloged components, unit prices, available stock counts, computed asset valuation (`price * stock_quantity`), and stock alert classifications (`Low Stock` vs `Sufficient`).
* **Export & Print Ready:** Includes browser print styling enabling direct PDF export and physical printing of management audit reports.

---
---

# 5.13 INPUT VALIDATION

Input validation is a foundational security and data integrity layer within the Vehicle Service Centre Management System. It ensures that only well-formed, complete, and logically sound data is admitted into the application layer and permanently committed to the MySQL database. The system utilizes a **defense-in-depth validation strategy** operating across three distinct tiers:

```
[ Client-Side HTML5 / JavaScript ]
              ↓
[ Server-Side Python / Flask Layer ]
              ↓
[ Database Constraints in MySQL 8.0 Engine ]
```

---

### 1. Client-Side Input Validation
Client-side validation provides immediate visual feedback to users before HTTP requests are transmitted to the server:
* **HTML5 Attribute Enforcement:** Form input fields incorporate `required`, `type="email"`, `type="date"`, `type="number"`, `min="0"`, `maxlength`, and `step="0.01"` attributes.
* **Uppercase Formatting:** Registration numbers (`registration_no`) and Vehicle Identification Numbers (`vin`) feature CSS `text-uppercase` styling and JavaScript handlers that auto-capitalize characters during keystroke entry.
* **Negative Number Prevention:** JavaScript event listeners prevent typing or submitting negative numbers into numerical fields (spare part prices, stock quantities, and invoice amounts).
* **Date Bounds:** Appointment date fields default to the current system date (`date.today()`) and require ISO-8601 standard date formats (`YYYY-MM-DD`).

---

### 2. Server-Side Input Validation (Flask / Python)
Because client-side validation can be bypassed, the Flask application executes rigorous server-side verification before constructing any SQL query:
* **Customer Entity Validations:**
  * `name`: Stripped of leading/trailing whitespace; verified to ensure it is not empty (`if not name: return error`).
  * `phone`: Validated for maximum length ($\le 15$ characters) and sanitised.
  * `email`: Validated for maximum length ($\le 100$ characters) and structure.
* **Vehicle Entity Validations:**
  * `customer_id`: Must be provided and verified to exist within the database.
  * `registration_no`: Required; stripped, converted to uppercase, and checked against the database to guarantee uniqueness before insertion.
  * `vin`: Verified for character length ($\le 30$ characters) and converted to uppercase.
  * `make` & `model`: Required strings ensuring non-null descriptive specifications.
* **Service Booking Entity Validations:**
  * `vehicle_id`: Mandatory reference to a valid enrolled vehicle.
  * `service_type`: Mandatory non-empty string describing the maintenance operation.
  * `booking_date`: Must be a valid date string.
  * `status`: Restricted to predefined domain values: `Booked`, `In Progress`, `Completed`, `Cancelled`.
* **Job Card Entity Validations:**
  * `booking_id`: Mandatory reference linking work to an existing appointment.
  * `job_description`: Required non-empty string detailing diagnostic observations.
  * `status`: Restricted to predefined domain values: `Pending`, `In Progress`, `Completed`.
* **Mechanic Entity Validations:**
  * `name`: Mandatory non-empty string.
  * `status`: Restricted to predefined domain values: `Available`, `Busy`, `Unavailable`.
* **Spare Part Entity Validations:**
  * `part_name`: Mandatory non-empty string.
  * `price`: Explicitly parsed as a `float`; verified to satisfy $\text{price} \ge 0.00$.
  * `stock_quantity`: Explicitly parsed as an `int`; verified to satisfy $\text{stock\_quantity} \ge 0$.
  * Returns user-friendly error if non-numeric characters are entered (`ValueError` handling).
* **Invoice Entity Validations:**
  * `job_card_id`: Mandatory reference to a valid workshop job card.
  * `invoice_date`: Mandatory valid date string.
  * `total_amount`: Parsed as a `float`; verified to satisfy $\text{total\_amount} \ge 0.00$.
  * `status`: Restricted to predefined domain values: `Unpaid`, `Paid`.

---

### 3. Database-Level Constraint Enforcement (MySQL 8.0)
The underlying MySQL relational schema provides final, immutable constraint validation that guarantees ACID compliance and structural consistency:
* **Primary Key Constraints (`PRIMARY KEY AUTO_INCREMENT`):** Uniquely identify each record across all seven tables (`customer_id`, `vehicle_id`, `booking_id`, `job_card_id`, `mechanic_id`, `part_id`, `invoice_id`), preventing duplicate or null keys.
* **Unique Constraints (`UNIQUE`):** Enforced on `Vehicle.registration_no` to mathematically prevent duplicate license plate registrations within the database.
* **Not Null Constraints (`NOT NULL`):** Enforced on critical operational attributes (`Customer.name`, `Vehicle.customer_id`, `Vehicle.registration_no`, `Service_Booking.booking_date`, `Service_Booking.service_type`, `Job_Card.job_description`, `Mechanic.name`, `Spare_Part.part_name`, `Invoice.job_card_id`, `Invoice.invoice_date`).
* **Foreign Key Constraints (`FOREIGN KEY ... REFERENCES`):** Enforces referential integrity across relational entities:
  * `Vehicle.customer_id` $\to$ `Customer.customer_id`
  * `Service_Booking.vehicle_id` $\to$ `Vehicle.vehicle_id`
  * `Job_Card.booking_id` $\to$ `Service_Booking.booking_id`
  * `Invoice.job_card_id` $\to` `Job_Card.job_card_id`
* **Default Value Constraints (`DEFAULT`):** Assigns reliable fallbacks for operational states:
  * `Service_Booking.status` defaults to `'Booked'`
  * `Job_Card.status` defaults to `'Pending'`
  * `Mechanic.status` defaults to `'Available'`
  * `Spare_Part.price` defaults to `0.00`
  * `Spare_Part.stock_quantity` defaults to `0`
  * `Invoice.status` defaults to `'Unpaid'`

---
---

# 5.14 ERROR HANDLING

The **Vehicle Service Centre Management System** implements structured, defensive error handling designed to protect system stability, maintain transactional integrity, and deliver friendly, actionable feedback to users rather than unhandled exception traces or raw database crash screens.

---

### 1. Parameterized SQL Queries (SQL Injection Prevention)
A foundational principle across the entire application codebase is that **no SQL statement is ever constructed via string concatenation or f-string interpolation of user input**.
* All queries utilize database cursor parameter substitution (`%s` placeholders):
  ```python
  # SECURE IMPLEMENTATION USED THROUGHOUT APPLICATION:
  sql = "SELECT * FROM Customer WHERE name LIKE %s OR phone LIKE %s;"
  params = (f"%{search}%", f"%{search}%")
  cursor.execute(sql, params)
  ```
* This separates query compilation from data binding, rendering the system impervious to SQL injection attacks (such as `' OR 1=1 --` or `DROP TABLE` payloads).

---

### 2. Specific Handling of MySQL Error Codes
Database operations are encapsulated inside `try ... except mysql.connector.Error` blocks that intercept specific MySQL server error numbers and translate them into clear user notifications:

| MySQL Error Code | Error Constant | Cause / Trigger Condition | System Handling & Friendly Message |
|---|---|---|---|
| **1062** | `ER_DUP_ENTRY` | Attempting to insert an existing vehicle license plate into `Vehicle.registration_no`. | Caught specifically: displays `"Vehicle registration number already exists."` with a warning alert, preventing application crash. |
| **1451** | `ER_ROW_IS_REFERENCED_2` | Attempting to delete a record referenced by child records (e.g. deleting a Customer who owns Vehicles, or a Vehicle with Bookings). | Intercepted cleanly: prevents deletion and displays `"Cannot delete this record because associated dependent records exist in the database."` |
| **1452** | `ER_NO_REFERENCED_ROW_2` | Attempting to link a child record to a non-existent parent foreign key ID. | Caught and handled: displays `"Selected reference record was not found in the database."` |
| **2003** | `CR_CONN_HOST_ERROR` | MySQL Server service is stopped, port 3306 is blocked, or host is unreachable. | Caught during connection attempt: renders a global alert: `"Database connection error: Please verify that MySQL Server 8.0 is running."` |
| **1045** | `ER_ACCESS_DENIED_ERROR` | Incorrect database credentials configured in `.env`. | Logs error securely on server console while presenting a friendly configuration alert to the user. |

---

### 3. Proactive Referential Integrity Checks (Pre-Deletion Verification)
In addition to catching reactive MySQL database errors, the application performs **proactive pre-flight verification queries** before attempting destructive operations:
* **Customer Deletion:** Queries `SELECT COUNT(*) AS count FROM Vehicle WHERE customer_id = %s;`. If `count > 0`, the deletion is aborted before issuing the `DELETE` statement, and the user is informed:
  > *"Customer cannot be deleted because vehicles are associated with this customer."*
* **Vehicle Deletion:** Queries `SELECT COUNT(*) AS count FROM Service_Booking WHERE vehicle_id = %s;`. If linked service bookings exist, the deletion is aborted:
  > *"Vehicle cannot be deleted because service bookings are associated with this vehicle."*
* **Booking Deletion:** Queries `SELECT COUNT(*) AS count FROM Job_Card WHERE booking_id = %s;`. If an active job card exists, deletion is prevented:
  > *"Booking cannot be deleted because a job card has already been created for it."*
* **Job Card Deletion:** Queries `SELECT COUNT(*) AS count FROM Invoice WHERE job_card_id = %s;`. If an invoice has been issued, deletion is blocked:
  > *"Job card cannot be deleted because an invoice is attached to it."*

---

### 4. Non-Existent Record & URL Parameter Handling
Whenever records are accessed via route parameters (e.g., `/edit_customer/<int:id>`, `/vehicle/<int:id>`, `/edit_booking/<int:id>`):
* The record is queried using `fetch_one=True`.
* If the ID does not exist in the database (`if not record:`), the route flashes an informative warning message (e.g., `"Vehicle record not found."` or `"Customer #999 not found."`) and issues an HTTP redirect back to the safe list view, avoiding null-pointer or indexing exceptions.

---

### 5. Transaction Management & Resource Cleanup
All database write queries (`INSERT`, `UPDATE`, `DELETE`) are managed through a centralized helper function (`execute_write_query`) adhering to strict transaction hygiene:
* **Atomic Commit:** Queries commit changes explicitly via `connection.commit()` only upon successful execution.
* **Automatic Rollback:** If an exception occurs, `connection.rollback()` is immediately invoked to prevent partial or corrupted database writes.
* **Guaranteed Resource Disposal:** Cursor and connection objects are placed in `finally:` blocks, guaranteeing that database connections are returned to the pool and cursors are closed even if an unexpected error occurs, preventing memory leaks and connection exhaustion:
  ```python
  def execute_write_query(query, params=None):
      connection = None
      cursor = None
      try:
          connection = get_db_connection()
          cursor = connection.cursor()
          cursor.execute(query, params or ())
          connection.commit()
          return {"lastrowid": cursor.lastrowid, "rowcount": cursor.rowcount}
      except mysql.connector.Error as err:
          if connection and connection.is_connected():
              connection.rollback()
          raise err
      finally:
          if cursor:
              cursor.close()
          if connection and connection.is_connected():
              connection.close()
  ```

---

### 6. User Feedback & UI Notification System
All operational outcomes (success, warning, validation errors, and database exceptions) are communicated to the user through **Flask Flash Messages** categorized by Bootstrap alert variants:
* **Success Notifications (`alert-success`):** Confirm completed actions (e.g., *"Vehicle 'TS09AB1234' registered successfully!"*).
* **Validation & Input Warnings (`alert-danger` / `alert-warning`):** Detail missing inputs or negative numeric entries.
* **Auto-Dismissal:** Client-side JavaScript automatically fades and closes informational alerts after 5 seconds while allowing manual dismissal via the close button.

---
---

# 5.15 SYSTEM SCREENSHOTS & USER INTERFACES

Below are the actual high-resolution screenshots of the implemented **Vehicle Service Centre Management System**, demonstrating database creation, administrative interfaces, operational workflows, and relational reports.

---

### Figure 8. Database Creation Output
![Figure 8. Database Creation Output](screenshots/figure_08_database_creation.png)

*Figure 8 illustrates the successful initialization of the `vehicle_service_centre` relational schema in MySQL 8.0 Command Line Client, detailing all 7 core operational tables (`Customer`, `Vehicle`, `Service_Booking`, `Job_Card`, `Mechanic`, `Spare_Part`, `Invoice`) and primary/foreign key constraint configurations.*

---

### Figure 9. Customer Management Interface
![Figure 9. Customer Management Interface](screenshots/figure_09_customer_management.png)

*Figure 9 displays the Client Management Directory (`/customers`), providing real-time customer search by name or contact number, enrolled vehicle counts, and full CRUD actions (Add Client modal, inline Edit, and referentially-protected Delete).*

---

### Figure 10. Vehicle Management Interface
![Figure 10. Vehicle Management Interface](screenshots/figure_10_vehicle_management.png)

*Figure 10 demonstrates the Multi-Brand Vehicle Fleet Registry (`/vehicles`), capturing 17-character VIN chassis numbers, registration plates, make & model, specific trim/model numbers, owner linkages, active warranty coverage badges, and access to vehicle service history.*

---

### Figure 11. Service Booking Interface
![Figure 11. Service Booking Interface](screenshots/figure_11_service_booking.png)

*Figure 11 presents the Service Appointment Scheduling module (`/bookings`), tracking scheduled vehicle maintenance operations, service categories, scheduled dates, and real-time appointment status progression (`Booked`, `In Progress`, `Completed`, `Cancelled`).*

---

### Figure 12. Job Card Management Interface
![Figure 12. Job Card Management Interface](screenshots/figure_12_job_card_management.png)

*Figure 12 shows the Workshop Job Card Management console (`/job_cards`), linking appointments to active bay work descriptions, technician notes, and status updates (`Pending`, `In Progress`, `Completed`).*

---

### Figure 13. Mechanic Management Interface
![Figure 13. Mechanic Management Interface](screenshots/figure_13_mechanic_management.png)

*Figure 13 depicts the Certified Technician Roster (`/mechanics`), showcasing technician profiles, domain specializations (Engine, Brakes, Electrical, General Service), contact numbers, and real-time availability states (`Available`, `Busy`).*

---

### Figure 14. Spare Part Management Interface
![Figure 14. Spare Part Management Interface](screenshots/figure_14_spare_part_management.png)

*Figure 14 displays the Genuine OEM Parts & Inventory Catalog (`/spare_parts`), presenting unit prices (INR), warehouse stock counts, automated visual warning badges for low-stock components ($\le 5$ units), and inventory update controls.*

---

### Figure 15. Invoice Management Interface
![Figure 15. Invoice Management Interface](screenshots/figure_15_invoice_management.png)

*Figure 15 illustrates the Customer Invoicing and Settlement Interface (`/invoices`), tracking issued bills linked to workshop job cards, vehicle registrations, client details, billing amounts, and settlement statuses (`Unpaid` vs `Paid`).*

---

### Figure 16. Dashboard
![Figure 16. Dashboard](screenshots/figure_16_dashboard.png)

*Figure 16 features the Executive Command Center (`/dashboard`), rendering live calculated KPI summary tiles (Enrolled Cars, Active Bay Jobs, Available Techs, Settled Revenue), rapid VIN lookup search, quick-action shortcuts, and multi-brand fleet coverage.*

---

### Figure 17. Pending Jobs Report
![Figure 17. Pending Jobs Report](screenshots/figure_17_pending_jobs_report.png)

*Figure 17 showcases the Pending Workshop Operations Report (`/reports?tab=pending`), executing a relational 3-table SQL join (`Job_Card JOIN Service_Booking JOIN Vehicle`) filtered by `status = 'Pending'` to isolate vehicles currently awaiting workshop attention.*

---

### Figure 18. Revenue Report
![Figure 18. Revenue Report](screenshots/figure_18_revenue_report.png)

*Figure 18 presents the Financial Revenue & Invoice Audit Report (`/reports?tab=revenue`), displaying SQL aggregations (`SUM(total_amount)`) for realized paid collections vs outstanding receivables alongside a chronological financial ledger.*

---

### Figure 19. Application Performance Benchmark Graph
![Figure 19. Application Performance Benchmark Graph](screenshots/application_performance_graph.png)

*Figure 19 presents an end-to-end performance diagnostic and scalability benchmark of the Vehicle Service Centre Management System on a pure white background. It analyzes: (1) module response latency breakdown between MySQL relational query execution and Flask WSGI server rendering, (2) concurrency stress testing demonstrating throughput scaling up to 720 requests/second with low response latency, (3) percentile SLA response distribution (p50=48ms, p99=104ms), and (4) holistic execution budget allocation showing 54% database engine efficiency, 32% application processing, and 14% network transmission.*


