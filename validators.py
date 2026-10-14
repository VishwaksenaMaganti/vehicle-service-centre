"""
=========================================================
AUTOCARE PRECISION - DATA VALIDATION MODULE (validators.py)
=========================================================
Provides comprehensive input validation rules for all entities,
CRUD operations, and database models.
"""

import re
from datetime import datetime

# Regex pattern for exactly 10 numeric digits (Indian & standard mobile formats)
PHONE_REGEX = re.compile(r"^[6-9]\d{9}$|^\d{10}$")

# RFC 5322 compliant simplified email regex
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Vehicle Registration Number regex (e.g. TS09AB1234, DL01A1234, MH-12-AB-1234)
REG_NO_REGEX = re.compile(r"^[A-Z]{2}[0-9A-Z -]{2,18}$", re.IGNORECASE)

# VIN regex (11 to 30 alphanumeric characters, typically 17)
VIN_REGEX = re.compile(r"^[A-HJ-NPR-Z0-9]{11,30}$", re.IGNORECASE)


def validate_phone(phone, required=False):
    """
    Validates phone number.
    Strictly enforces:
    - Cannot exceed 10 digits.
    - Must be exactly 10 numeric digits.
    - Rejects letters, symbols, negative numbers, or extra digits.
    """
    if not phone or not phone.strip():
        if required:
            return False, "Phone number is required."
        return True, None

    cleaned = phone.strip().replace(" ", "").replace("-", "")

    if len(cleaned) > 10:
        return False, f"Invalid phone number! Length is {len(cleaned)} digits. Phone number cannot exceed 10 digits."

    if len(cleaned) < 10:
        return False, f"Invalid phone number! Length is {len(cleaned)} digits. Phone number must be exactly 10 digits."

    if not cleaned.isdigit():
        return False, "Invalid phone number! Phone number must contain only numeric digits (0-9)."

    return True, cleaned


def validate_email(email, required=False):
    """Validates email format and maximum length."""
    if not email or not email.strip():
        if required:
            return False, "Email address is required."
        return True, None

    cleaned = email.strip()
    if len(cleaned) > 100:
        return False, "Email address cannot exceed 100 characters."

    if not EMAIL_REGEX.match(cleaned):
        return False, "Invalid email address format (e.g. client@example.com)."

    return True, cleaned.lower()


def validate_name(name, field_name="Name", min_len=2, max_len=100):
    """Validates a textual name (person, part, etc.)."""
    if not name or not name.strip():
        return False, f"{field_name} is required and cannot be blank."

    cleaned = name.strip()
    if len(cleaned) < min_len:
        return False, f"{field_name} must be at least {min_len} characters long."

    if len(cleaned) > max_len:
        return False, f"{field_name} cannot exceed {max_len} characters."

    # Must contain at least one alphanumeric character
    if not any(c.isalnum() for c in cleaned):
        return False, f"{field_name} must contain valid letters or numbers."

    return True, cleaned


def validate_registration_no(reg_no):
    """Validates vehicle registration plate."""
    if not reg_no or not reg_no.strip():
        return False, "Vehicle registration number is required."

    cleaned = reg_no.strip().upper().replace(" ", "")
    if len(cleaned) < 4:
        return False, "Registration number must be at least 4 characters."

    if len(cleaned) > 20:
        return False, "Registration number cannot exceed 20 characters."

    if not cleaned.isalnum():
        return False, "Registration number must be alphanumeric (no special symbols)."

    return True, cleaned


def validate_vin(vin, required=False):
    """Validates 11-30 character Vehicle Identification Number (VIN)."""
    if not vin or not vin.strip():
        if required:
            return False, "VIN (Vehicle Identification Number) is required."
        return True, None

    cleaned = vin.strip().upper()
    if len(cleaned) < 11:
        return False, f"VIN must be at least 11 characters (standard is 17). Entered: {len(cleaned)}."

    if len(cleaned) > 30:
        return False, f"VIN cannot exceed 30 characters. Entered: {len(cleaned)}."

    if not re.match(r"^[A-Z0-9]+$", cleaned):
        return False, "VIN must contain only alphanumeric characters (A-Z, 0-9)."

    return True, cleaned


def validate_price(price_input, field_name="Price", min_val=0.0, max_val=10000000.0):
    """Validates decimal monetary price."""
    if price_input is None or str(price_input).strip() == "":
        return False, f"{field_name} is required."

    try:
        val = float(str(price_input).strip())
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid numeric amount."

    if val < min_val:
        return False, "Price and stock quantity cannot be negative."

    if val > max_val:
        return False, f"{field_name} exceeds maximum allowable threshold (₹{max_val:,.2f})."

    return True, round(val, 2)


def validate_quantity(qty_input, field_name="Quantity", min_val=0, max_val=100000):
    """Validates integer stock quantity."""
    if qty_input is None or str(qty_input).strip() == "":
        return False, f"{field_name} is required."

    try:
        val_str = str(qty_input).strip()
        if "." in val_str:
            return False, f"{field_name} must be a whole integer, not a decimal."
        val = int(val_str)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid whole integer."

    if val < min_val:
        return False, "Price and stock quantity cannot be negative."

    if val > max_val:
        return False, f"{field_name} exceeds maximum limit of {max_val} units."

    return True, val


def validate_date_string(date_str, field_name="Date"):
    """Validates date string in YYYY-MM-DD format."""
    if not date_str or not date_str.strip():
        return False, f"{field_name} is required."

    try:
        parsed_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        if parsed_date.year < 2000 or parsed_date.year > 2050:
            return False, f"{field_name} year must be between 2000 and 2050."
        return True, str(parsed_date)
    except ValueError:
        return False, f"{field_name} must be in valid YYYY-MM-DD format."


def validate_status(status_str, allowed_statuses, field_name="Status"):
    """Validates that a status belongs to the permissible enumeration."""
    if not status_str or not status_str.strip():
        return False, f"{field_name} is required."

    cleaned = status_str.strip()
    if cleaned not in allowed_statuses:
        return False, f"Invalid {field_name} '{cleaned}'. Permitted values: {', '.join(allowed_statuses)}."

    return True, cleaned
