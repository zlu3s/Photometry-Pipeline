# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 09:07:47 2023

@author: ablock
"""

import sqlite3
from datetime import datetime

def fetch_tles(database_path, norad_id, date_after):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    dbCursor = conn.cursor()

    # Set up the query and parameters
    query = """
    SELECT tle 
    FROM tles 
    WHERE norad_id = ? 
    AND epoch > ? 
    ORDER BY julianday(epoch) ASC
    """
    params = (norad_id, date_after.strftime('%Y-%m-%d %H:%M:%S'))

    # Execute the query
    dbCursor.execute(query, params)

    # Fetch the TLEs
    tles = [s[0] for s in dbCursor]

    # Close the database connection
    conn.close()

    return tles

if __name__ == "__main__":
    database_path = "D:\\UKRIT_2021\\Database\\ukirt.db"  # Change this to the path of your SQLite database
    norad_id = 38978
    date_after = datetime.strptime("2021-06-01", "%Y-%m-%d")

    tles = fetch_tles(database_path, norad_id, date_after)
    
    if tles:
        print(f"TLEs for NORAD ID {norad_id} after {date_after.date()} are:")
        for tle in tles:
            print(tle)
    else:
        print(f"No TLEs found for NORAD ID {norad_id} after {date_after.date()}.")

