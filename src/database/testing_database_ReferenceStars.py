# databaseAccessExample.py
#
# Example access script for SQLite database
# 
# More resources:
# https://www.tutorialspoint.com/sqlite/sqlite_python.htm
# https://www.w3schools.com/sql/
# 



import sqlite3
import numpy as np





databaseFile = "D:\\UKRIT_2021\\Database\\ukirt.db"
plotlist = ['99999 Sidereal']
sattype =''
index = 0
sat_name,norad=[],[]
filterband,mag,magnitude_error,obs_time,elongation_list = [],[],[],[],[]
visits = 0
found_sats = []




# Open database file (will create new one if not exist)
try:
	print("Opening database...")
	conn = sqlite3.connect(databaseFile)
except Exception as e:
	print("Failed!")
	print(e)
	exit()

print("Success!")


# Cursor for accessing the DB
cursor = conn.cursor()


select_string_statement="""SELECT images.msb_title,images.filter,images.start_time,referenceStars.zeropoint,images.airmass,referenceStars.zeropoint_error
			FROM images INNER JOIN referenceStars ON images.id = referenceStars.image_id
			WHERE images.msb_title LIKE "%99999%" AND referenceStars.rejected = 0
			ORDER BY images.start_time;"""

# Print select items from combination of sats and targets and images tables
cursor.execute(select_string_statement)
for s in cursor:
	print(s[0],s[1],s[2],s[3],s[4],s[5])
			
			

# Commit changes to database and close
conn.commit()
conn.close()
