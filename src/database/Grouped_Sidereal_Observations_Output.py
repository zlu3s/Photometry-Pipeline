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
import datetime as dt
import os




databaseFile = "D:\\UKRIT_2021\\Database\\ukirt.db"
grouping_time = 36000 #10 hours
plotlist = []
#plotlist = [10684,11054,11141,15039,45854,46826,20302,20830,24876,26605,28129,34661,21930,22446,22581,23027,37753]
index = 0
sat_name,norad=[],[]
filterband,mag,magnitude_error,obs_time,elongation_list,tle,mag_err = [],[],[],[],[],[],[]
zp,zp_err,RA,Dec,airmass,fwhm,filename = [],[],[],[],[],[],[]
nights = 0
found_sats = []
totalobs,total_nights=0,0





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
#Output Columns
# TLE s[11]
#  s[0]    s[1]     s[2]    s[3] s[4]s[5]     s[6]       s[7] s[8]  s[9]  s[10]  s[12]        s[13]s[14]
#SatNorad SatName Date-Obs Filter RA Dec SolarElongation ZP ZP_err Mag Mag_err  filename  RA_predicated   Dec_predicated
#AND images.start_time > strftime('%Y-%m-%d:%s','2021-01-01')

select_string_statement= """
SELECT 
    images.start_time,
    images.filter,
    referenceStars.ra,
    referenceStars.decl,
    referenceStars.airmass,
    referenceStars.fwhm,
    referenceStars.zeropoint,
    referenceStars.zeropoint_error,
    referenceStars.magnitude,
    referenceStars.magnitude_error,
    images.imageFile
FROM 
    referenceStars
JOIN 
    images ON referenceStars.image_id = images.id
WHERE 
    referenceStars.rejected = 0 AND referenceStars.magnitude IS NOT NULL
	ORDER BY images.start_time;
"""
#   s[0]     s[1]    s[2]  s[3]   s[4]    s[5]    s[6]         s[7]             s[8]        s[9]              s[10]
#Date-Obs   Filter   RA   Dec   Airmass   FWHM   Zeropoint  Zeropoint Error   Magnitude   Magnitude Error   Filename
# Print select items from combination of sats and targets and images tables
cursor.execute(select_string_statement)
for s in cursor:
	
	if index == 0: #initialize first time
		group_start_time = dt.datetime.strptime(s[0], '%Y-%m-%d %H:%M:%S.%f')
	current_time = dt.datetime.strptime(s[0], '%Y-%m-%d %H:%M:%S.%f')
	timedifference = (current_time - group_start_time).total_seconds()
	if timedifference >= 0 and timedifference < grouping_time: #finding >= zero was subtle
		#make lists
		obs_time.append(dt.datetime.strptime(s[0], '%Y-%m-%d %H:%M:%S.%f')) 
		filterband.append(s[1])
		RA.append(s[2]/15)
		Dec.append(s[3])
		airmass.append(s[4])
		fwhm.append(s[5])
		zp.append(s[6])
		zp_err.append(s[7])
		mag.append(s[8])
		mag_err.append(s[9])
		filename.append(s[10])

		index = index + 1
		
	elif timedifference > grouping_time:
		for i,filterindex in enumerate(filterband):
			if filterindex in ['J','H','K']:
				file_path = 'D:\\UKRIT_2021\\_Output\\Starfield_Field_' + filterindex + '_' + group_start_time.strftime('%Y-%m-%d_%H-%M-%S')+'.txt'
				is_new_file = not os.path.exists(file_path)
				with open(file_path, "a") as file:
					if is_new_file:
						header_format =                 '{:<22}   {:<6}   {:<10}   {:<10}   {:<7}   {:<7}  {:<7}   {:<7}   {:<7}   {:<7}   {:<30}\n'
						file.write(header_format.format('Date-Obs', 'Filter', 'RA', 'Dec', 'Airmass', 'FWHM', 'ZP', 'ZP_err', 'Mag', 'Mag_err', 'File'))
						
					data_format = '{:<22}   {:<6}   {:<10.5f}   {:<10.3f}   {:<7.2f}   {:<7.2f}  {:<7.2f}   {:<7.2f}   {:<7.2f}   {:<7.2f}   {:<30}\n'
					file.write(data_format.format(obs_time[i].strftime('%Y-%m-%d %H:%M:%S'),filterband[i], RA[i], Dec[i], airmass[i], fwhm[i], zp[i], zp_err[i], mag[i], mag_err[i],filename[i]))
					
		nights = nights +1
		total_nights = total_nights+1
			
		filterband,obs_time,mag,mag_err,zp,zp_err,RA,Dec,filename,airmass,fwhm= [],[],[],[],[],[],[],[],[],[],[]
		group_start_time = current_time  #reset the group start time so that there so no observations are missed
		index = 0
		
		#Due to the way this is counted, the current value of s[3] would have been skipped. By appending it and
		#the other related bits of information everything should be accounted for
		#to test put print(s[2],s[3]) below the satellite loop for the real values and print the mag list in the elif statement
		obs_time.append(dt.datetime.strptime(s[0], '%Y-%m-%d %H:%M:%S.%f')) 
		filterband.append(s[1])
		RA.append(s[2])
		Dec.append(s[3])
		airmass.append(s[4])
		fwhm.append(s[5])
		zp.append(s[6])
		zp_err.append(s[7])
		mag.append(s[8])
		mag_err.append(s[9])
		filename.append(s[10])

			

for i,filterindex in enumerate(filterband):
	if filterindex in ['J','H','K']:
		file_path ='D:\\UKRIT_2021\\_Output\\Starfield_Field_' + filterindex + '_' + group_start_time.strftime('%Y-%m-%d_%H-%M-%S')+'.txt'
		is_new_file = not os.path.exists(file_path)
		with open(file_path, "a") as file:
			data_format = '{:<22}   {:<6}   {:<10.5f}   {:<10.3f}   {:<7.2f}   {:<7.2f}  {:<7.2f}   {:<7.2f}   {:<7.2f}   {:<7.2f}   {:<30}\n'
			file.write(data_format.format(obs_time[i].strftime('%Y-%m-%d %H:%M:%S'),filterband[i], RA[i], Dec[i], RA[i], airmass[i], Dec[i], fwhm[i], zp[i], zp_err[i], mag[i], mag_err[i],filename[i]))
			
nights = nights+1


print("{} nights of star data.".format(nights))

index = 0
nights = 0

if plotlist:
	for i in range(len(plotlist)):
		if plotlist[i] not in found_sats:
			print('{} has no output because it was either not in the database or all of its images were rejected.'.format(plotlist[i]))
# Commit changes to database and close
print('Total Number of Nights of Observing in this aggregated data: {}.'.format(total_nights))
print('Total Number of Observations in this period: {}.'.format(len(filename)))
conn.commit()
conn.close()
