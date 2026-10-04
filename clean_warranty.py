from database import execute_write_query

execute_write_query("UPDATE Vehicle SET warranty_details = 'Active (5-Year / 100,000 km Comprehensive)' WHERE vehicle_id = 1;")
execute_write_query("UPDATE Vehicle SET warranty_details = 'Active (Porsche Approved Warranty till Oct 2027)' WHERE vehicle_id = 2;")
execute_write_query("UPDATE Vehicle SET warranty_details = 'Active (3-Year / Unlimited KM Factory Warranty)' WHERE vehicle_id = 3;")
execute_write_query("UPDATE Vehicle SET warranty_details = 'Active (Toyota Shield Protection till Dec 2028)' WHERE vehicle_id = 4;")
execute_write_query("UPDATE Vehicle SET warranty_details = 'Active (5-Year / 120,000 km Comprehensive)' WHERE vehicle_id = 5;")

print("Updated warranty details cleanly.")
