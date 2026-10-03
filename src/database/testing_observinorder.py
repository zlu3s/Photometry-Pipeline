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
plotlist = []
sattype =''
index = 0
sat_name,norad=[],[]
filterband,mag,magnitude_error,obs_time,elongation_list = [],[],[],[],[]
visits = 0
found_sats = []
current_satname = ''


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

cursor.execute("SELECT norad_id, name FROM sats")
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type LIKE 'HS-376%';" )
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type LIKE '%RB%';" )
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type  NOT LIKE 'HS-376%';" )
#cursor.execute( "SELECT norad_id, name FROM sats WHERE name LIKE '%BREEZE%';" )
for s in cursor:
	if plotlist:
		if s[0] in plotlist:
			sat_name.append(s[1])
			norad.append(s[0])
	else:
		sat_name.append(s[1])
		norad.append(s[0])
		

#AND images.start_time > strftime('%Y-%m-%d:%s','2021-01-01')
select_string_statement="""SELECT sats.norad_id, images.filter, images.start_time, targets.magnitude, targets.sun_elong_predicted,sats.name,targets.sextractor, targets.rejected
			FROM ((sats INNER JOIN targets ON sats.id = targets.target_id) INNER JOIN images ON targets.image_id = images.id)
			WHERE (images.start_time > strftime('%Y-%m-%d:%s','2023-05-16')
				  )
			ORDER BY images.start_time;"""

# Print select items from combination of sats and targets and images tables
cursor.execute(select_string_statement)
for s in cursor:
	#print(s[0],s[1],s[2],s[3],s[4],s[5],s[6],s[7])
	if current_satname != s[0]:
		current_satname = s[0]
		print('{}  {}'.format(current_satname,s[2]))
				

# Commit changes to database and close
conn.commit()
conn.close()
