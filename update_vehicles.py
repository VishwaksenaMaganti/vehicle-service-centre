from database import execute_write_query, execute_read_query

execute_write_query("UPDATE Vehicle SET make = %s, model = %s WHERE vehicle_id = %s;", ('BMW', '7 Series Sedan', 1))
execute_write_query("UPDATE Vehicle SET make = %s, model = %s WHERE vehicle_id = %s;", ('Porsche', '911 Carrera', 2))
execute_write_query("UPDATE Vehicle SET make = %s, model = %s WHERE vehicle_id = %s;", ('Porsche', 'Taycan Turbo', 3))
execute_write_query("UPDATE Vehicle SET make = %s, model = %s WHERE vehicle_id = %s;", ('BMW', 'i7 xDrive60', 4))
execute_write_query("UPDATE Vehicle SET make = %s, model = %s WHERE vehicle_id = %s;", ('Porsche', '718 Boxster', 5))

# Also update Job Card descriptions if they referenced old cars
execute_write_query("UPDATE Job_Card SET job_description = %s WHERE job_card_id = 1;", ('BMW 7 Series Comprehensive Service and Oil Replacement',))
execute_write_query("UPDATE Job_Card SET job_description = %s WHERE job_card_id = 2;", ('Porsche 911 Carrera Mobil 1 Oil & Filter Replacement',))
execute_write_query("UPDATE Job_Card SET job_description = %s WHERE job_card_id = 3;", ('Porsche Taycan High-Voltage Diagnostics and Brake Inspection',))
execute_write_query("UPDATE Job_Card SET job_description = %s WHERE job_card_id = 4;", ('BMW i7 Annual Maintenance & Software Diagnostics',))
execute_write_query("UPDATE Job_Card SET job_description = %s WHERE job_card_id = 5;", ('Porsche 718 Boxster Performance Exhaust & Engine Tuning',))

vehicles = execute_read_query("SELECT vehicle_id, registration_no, make, model FROM Vehicle;")
print("Updated Vehicles:")
for v in vehicles:
    print(v)
