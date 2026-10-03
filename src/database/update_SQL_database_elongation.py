# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 22:58:17 2025

@author: ngc1535
"""

import sqlite3

# Define database path
db_path = "D:\\UKRIT_2021\\Database\\ukirt.db"

# Define parameters
norad_id = 39479
start_time = "2025-02-21 07:00:00"  # Start of time range
end_time = "2025-02-22 16:00:00"  # End of time range
new_elongation_value = 168.56  # Replace with the correct value

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    UPDATE targets
    SET sun_elong_predicted = ?
    WHERE target_id IN (
        SELECT id FROM sats WHERE norad_id = ?
    )
    AND image_id IN (
        SELECT id FROM images WHERE start_time BETWEEN ? AND ?
    )
""", (new_elongation_value, norad_id, start_time, end_time))


# Commit changes
conn.commit()
print(f"Updated {cursor.rowcount} records.")

# Close connection
conn.close()