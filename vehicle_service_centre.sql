-- =========================================================
-- VEHICLE SERVICE CENTRE MANAGEMENT SYSTEM
-- Database Version 1
-- MySQL
-- =========================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS vehicle_service_centre;

USE vehicle_service_centre;


-- =========================================================
-- 1. CUSTOMER
-- =========================================================

CREATE TABLE IF NOT EXISTS Customer (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100)
);


-- =========================================================
-- 2. VEHICLE
-- =========================================================

CREATE TABLE IF NOT EXISTS Vehicle (
    vehicle_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    registration_no VARCHAR(20) NOT NULL UNIQUE,
    vin VARCHAR(30),
    make VARCHAR(50),
    model VARCHAR(50),
    model_number VARCHAR(50),
    warranty_details VARCHAR(100) DEFAULT 'Standard Warranty Active',

    CONSTRAINT fk_vehicle_customer
        FOREIGN KEY (customer_id)
        REFERENCES Customer(customer_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- =========================================================
-- 3. SERVICE BOOKING
-- =========================================================

CREATE TABLE IF NOT EXISTS Service_Booking (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_id INT NOT NULL,
    booking_date DATE NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Booked',

    CONSTRAINT fk_booking_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES Vehicle(vehicle_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- =========================================================
-- 4. JOB CARD
-- =========================================================

CREATE TABLE IF NOT EXISTS Job_Card (
    job_card_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    job_description VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Pending',

    CONSTRAINT fk_job_booking
        FOREIGN KEY (booking_id)
        REFERENCES Service_Booking(booking_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- =========================================================
-- 5. MECHANIC
-- =========================================================

CREATE TABLE IF NOT EXISTS Mechanic (
    mechanic_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    phone VARCHAR(15),
    status VARCHAR(30) NOT NULL DEFAULT 'Available'
);


-- =========================================================
-- 6. SPARE PART
-- =========================================================

CREATE TABLE IF NOT EXISTS Spare_Part (
    part_id INT PRIMARY KEY AUTO_INCREMENT,
    part_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    stock_quantity INT NOT NULL DEFAULT 0
);


-- =========================================================
-- 7. INVOICE
-- =========================================================

CREATE TABLE IF NOT EXISTS Invoice (
    invoice_id INT PRIMARY KEY AUTO_INCREMENT,
    job_card_id INT NOT NULL,
    invoice_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(30) NOT NULL DEFAULT 'Unpaid',

    CONSTRAINT fk_invoice_job
        FOREIGN KEY (job_card_id)
        REFERENCES Job_Card(job_card_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- =========================================================
-- SAMPLE DATA
-- =========================================================

-- CUSTOMER DATA

INSERT INTO Customer (name, phone, email) VALUES
('Rahul Kumar', '9876543210', 'rahul@gmail.com'),
('Priya Sharma', '9876501234', 'priya@gmail.com'),
('Arjun Reddy', '9123456789', 'arjun@gmail.com'),
('Sneha Rao', '9988776655', 'sneha@gmail.com'),
('Vikram Singh', '9012345678', 'vikram@gmail.com');


-- VEHICLE DATA

INSERT INTO Vehicle
(customer_id, registration_no, vin, make, model, model_number, warranty_details)
VALUES
(1, 'TS09AB1234', 'MA1TA2845N4018291', 'Honda', 'City', 'ZX 1.5 i-VTEC CVT', 'Active (5-Year / 120,000 km Comprehensive)'),
(2, 'TS10CD5678', 'WP0AA2994NS240182', 'Porsche', '911 Carrera', 'Carrera S Coupe 3.0L Twin-Turbo', 'Active (Porsche Approved Warranty till Oct 2027)'),
(3, 'AP16EF9012', 'MALC381CLPM102948', 'Hyundai', 'Creta', 'SX(O) 1.5 Turbo DCT', 'Active (3-Year / Unlimited KM Factory Warranty)'),
(4, 'TS11GH3456', 'MBJ11EB84MN492019', 'Toyota', 'Fortuner', '2.8 4x4 AT Legender', 'Active (Toyota Shield Protection till Dec 2028)'),
(5, 'AP07JK7890', 'MAKGM668LNA390123', 'Honda', 'City', 'ZX 1.5 i-VTEC CVT', 'Active (5-Year / 120,000 km Comprehensive)');


-- SERVICE BOOKINGS

INSERT INTO Service_Booking
(vehicle_id, booking_date, service_type, status)
VALUES
(1, '2026-09-20', 'General Service', 'Booked'),
(2, '2026-09-20', 'Oil Change', 'Completed'),
(3, '2026-09-21', 'Brake Inspection', 'Booked'),
(4, '2026-09-21', 'General Service', 'In Progress'),
(5, '2026-09-22', 'Engine Check', 'Booked');


-- JOB CARDS

INSERT INTO Job_Card
(booking_id, job_description, status)
VALUES
(1, 'General service and engine oil replacement', 'Pending'),
(2, 'Engine oil and filter replacement', 'Completed'),
(3, 'Inspect front and rear brakes', 'Pending'),
(4, 'General vehicle service', 'In Progress'),
(5, 'Check engine performance and diagnostics', 'Pending');


-- MECHANICS

INSERT INTO Mechanic
(name, specialization, phone, status)
VALUES
('Ramesh Kumar', 'Engine Specialist', '9877001122', 'Available'),
('Suresh Rao', 'Brake Specialist', '9877002233', 'Busy'),
('Mahesh Kumar', 'General Service', '9877003344', 'Available'),
('Kiran Reddy', 'Electrical Specialist', '9877004455', 'Available');


-- SPARE PARTS

INSERT INTO Spare_Part
(part_name, price, stock_quantity)
VALUES
('Engine Oil 5W-30', 450.00, 25),
('Oil Filter', 350.00, 15),
('Air Filter', 500.00, 10),
('Brake Pad Set', 1800.00, 8),
('Spark Plug', 250.00, 20),
('Coolant', 400.00, 12);


-- INVOICES

INSERT INTO Invoice
(job_card_id, invoice_date, total_amount, status)
VALUES
(2, '2026-09-20', 2500.00, 'Paid'),
(4, '2026-09-21', 3200.00, 'Unpaid');


-- =========================================================
-- VERIFY DATABASE
-- =========================================================

SHOW TABLES;


-- View sample data

SELECT * FROM Customer;

SELECT * FROM Vehicle;

SELECT * FROM Service_Booking;

SELECT * FROM Job_Card;

SELECT * FROM Mechanic;

SELECT * FROM Spare_Part;

SELECT * FROM Invoice;


-- =========================================================
-- BASIC JOIN FOR TESTING
-- =========================================================

SELECT
    c.name AS customer_name,
    v.registration_no,
    v.make,
    v.model,
    sb.service_type,
    sb.status
FROM Customer c
JOIN Vehicle v
    ON c.customer_id = v.customer_id
JOIN Service_Booking sb
    ON v.vehicle_id = sb.vehicle_id;


-- =========================================================
-- PENDING JOBS
-- =========================================================

SELECT
    jc.job_card_id,
    v.registration_no,
    jc.job_description,
    jc.status
FROM Job_Card jc
JOIN Service_Booking sb
    ON jc.booking_id = sb.booking_id
JOIN Vehicle v
    ON sb.vehicle_id = v.vehicle_id
WHERE jc.status = 'Pending';


-- =========================================================
-- TOTAL REVENUE
-- =========================================================

SELECT
    SUM(total_amount) AS total_revenue
FROM Invoice
WHERE status = 'Paid';