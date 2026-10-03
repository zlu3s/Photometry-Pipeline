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
import os,hashlib






databaseFile = "D:\\UKRIT_2021\\Database\\ukirt.db"
plotlist = [58204]
sattype =''
index = 0
sat_name,norad=[],[]
filterband,mag,magnitude_error,obs_time,elongation_list = [],[],[],[],[]
visits = 0
found_sats = []
current_satname = ''
zp_Z,zp_Y,zp_K,zp_J,zp_H,zperr_Z,zperr_Y,zperr_K,zperr_J,zperr_H = [],[],[],[],[],[],[],[],[],[]

print("ABS PATH:", os.path.abspath(databaseFile))
print("SIZE:", os.path.getsize(databaseFile))
print("MTIME:", os.path.getmtime(databaseFile))

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()
print("MD5:", md5(databaseFile))
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

cursor.execute("""
SELECT id, norad_id, name
FROM sats
WHERE norad_id = 58204;
""")

for row in cursor:
    print(row)


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
for satdex,satellite in enumerate(norad):
	select_string_statement="""SELECT sats.norad_id,sats.name, images.filter, images.start_time, targets.magnitude, targets.zeropoint,targets.zeropoint_error,targets.rejected,targets.sextractor,targets.sun_elong_predicted
				FROM ((sats INNER JOIN targets ON sats.id = targets.target_id) INNER JOIN images ON targets.image_id = images.id)
				WHERE (sats.norad_id = """+str(satellite)+"""
				AND targets.rejected < 1
				AND targets.magnitude IS NOT NULL
				AND images.airmass < 3
				AND targets.sextractor = 0
					  )
				ORDER BY images.start_time;"""

	# Print select items from combination of sats and targets and images tables
	cursor.execute(select_string_statement)
	for s in cursor:
		#print(s[0],s[1],s[2],s[3],s[4],s[5],s[6],s[7],s[9])
		if s[2] =='Z':
			zp_Z.append(s[5])
			zperr_Z.append(s[6])
		if s[2] =='Y':
			zp_Y.append(s[5])
			zperr_Y.append(s[6])
		if s[2] =='J':
			zp_J.append(s[5])
			zperr_J.append(s[6])
		if s[2] =='H':
			zp_H.append(s[5])
			zperr_H.append(s[6])
		if s[2] =='K':
			zp_K.append(s[5])
			zperr_K.append(s[6])				
print('Z  '+str(np.median(zp_Z))+'   '+str(np.median(zperr_Z)))
print('Y  '+str(np.median(zp_Y))+'   '+str(np.median(zperr_Y)))
print('J  '+str(np.median(zp_J))+'   '+str(np.median(zperr_J)))
print('H  '+str(np.median(zp_H))+'   '+str(np.median(zperr_H)))
print('K  '+str(np.median(zp_K))+'   '+str(np.median(zperr_K)))
# Commit changes to database and close
conn.commit()
conn.close()
