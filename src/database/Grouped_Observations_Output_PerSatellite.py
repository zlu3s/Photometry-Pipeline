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
grouping_time = 1200 #20 hours
plotlist = []
#plotlist = [10684,11054,11141,15039,45854,46826,20302,20830,24876,26605,28129,34661,21930,22446,22581,23027,37753]
index = 0
sat_name,norad=[],[]
filterband,mag,magnitude_error,obs_time,elongation_list,tle,mag_err = [],[],[],[],[],[],[]
zp,zp_err,RA,Dec,RA_pred,Dec_pred,filename = [],[],[],[],[],[],[]
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

# Print only norad_id, name from sats table only for HS-376 models
#cursor.execute("SELECT norad_id, name FROM sats")
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type LIKE '%GPS%';" )
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type LIKE '%RB%';" )
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type  NOT LIKE 'HS-376%';" )
cursor.execute( "SELECT norad_id, name FROM sats WHERE name LIKE '%NAV%';" )
for s in cursor:
	if plotlist:
		if s[0] in plotlist:
			sat_name.append(s[1])
			norad.append(s[0])
	else:
		sat_name.append(s[1])
		norad.append(s[0])
		


#Output Columns
# TLE s[11]
#  s[0]    s[1]     s[2]    s[3] s[4]s[5]     s[6]       s[7] s[8]  s[9]  s[10]  s[12]        s[13]s[14]
#SatNorad SatName Date-Obs Filter RA Dec SolarElongation ZP ZP_err Mag Mag_err  filename  RA_predicated   Dec_predicated
#AND images.start_time > strftime('%Y-%m-%d:%s','2021-01-01')
for satdex,satellite in enumerate(norad):
	select_string_statement="""SELECT sats.norad_id,sats.name,images.start_time, images.filter,images.tel_ra,images.tel_dec, targets.sun_elong_predicted,targets.zeropoint,targets.zeropoint_error,targets.magnitude,targets.magnitude_error,tles.tle,images.imageFile,targets.ra_predicted,targets.decl_predicted
				FROM (((sats INNER JOIN targets ON sats.id = targets.target_id) INNER JOIN images ON targets.image_id = images.id) INNER JOIN tles ON targets.tle_id = tles.id)
				WHERE (sats.norad_id = """+str(satellite)+"""
					  AND targets.rejected < 1 
					  AND targets.magnitude IS NOT NULL
					  AND targets.sextractor = 0
					  )
				ORDER BY images.start_time;"""

	# Print select items from combination of sats and targets and images tables
	cursor.execute(select_string_statement)
	for s in cursor:
		totalobs = totalobs +1
		if s[0] == satellite:
			if index == 0: #initialize first time
				satname = s[1]
				noradname = str(s[0])
				found_sats.append(int(noradname))
				group_start_time = dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f')
				tle=(s[11])
			current_time = dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f')
			timedifference = (current_time - group_start_time).total_seconds()
			if timedifference >= 0 and timedifference < grouping_time: #finding >= zero was subtle
				#make lists 
				filterband.append(s[3])
				mag.append(s[9])
				mag_err.append(s[10])
				zp.append(s[7])
				zp_err.append(s[8])
				RA.append(s[4])
				Dec.append(s[5])
				filename.append(s[12])
				RA_pred.append(s[13]/15) #RA predicted in database is in degrees and not decimal hours
				Dec_pred.append(s[14])
				obs_time.append(dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f'))
				if s[6] == None:
					elongation_list.append(np.nan)
				else:
					elongation_list.append(s[6])  #also record elongation
				index = index + 1
			elif timedifference > grouping_time:
				for i,filterindex in enumerate(filterband):
					if filterindex in ['J','H','K']:
						file_path = 'D:\\UKRIT_2021\\_Output\\' + noradname + '_Filter_' + filterindex + '_' + group_start_time.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
						is_new_file = not os.path.exists(file_path)
						with open(file_path, "a") as file:
							if is_new_file:
								file.write(noradname+' '+satname+'\n'+tle.strip('UNKNOWN\n')+'\n--------------------------------------------------------------------\n')
								header_format = '{:<5}   {:<28}   {:<22}   {:<6}   {:<10}   {:<12}   {:<10}   {:<12}  {:<10}   {:<7}   {:<7}   {:<7}   {:<7}\n'
								file.write(header_format.format('NORAD', 'Descriptive Name', 'DATE-OBS', 'Filter', 'RA', 'RA Predicted', 'Dec', 'Dec Predicted', 'Sol Elong', 'Zero Pt', 'Zpt Err', 'Mag', 'Mag Err'))
								
							data_format = '{:<5}   {:<28}   {:<22}   {:<6}   {:<10.5f}   {:<12.5f}   {:<10.3f}   {:<12.3f}   {:<10.2f}   {:<7.2f}   {:<7.2f}   {:<7.2f}   {:<7.2f}\n'
							file.write(data_format.format(noradname, satname, obs_time[i].strftime('%Y-%m-%d %H:%M:%S'), filterindex, RA[i], RA_pred[i], Dec[i], Dec_pred[i], elongation_list[i], zp[i], zp_err[i], mag[i], mag_err[i]))
							
				nights = nights +1
				total_nights = total_nights+1
					
				filterband,obs_time,elongation_list,mag,mag_err,zp,zp_err,RA,Dec,filename,RA_pred,Dec_pred= [],[],[],[],[],[],[],[],[],[],[],[]
				group_start_time = current_time  #reset the group start time so that there so no observations are missed
				index = 0
				
				#Due to the way this is counted, the current value of s[3] would have been skipped. By appending it and
				#the other related bits of information everything should be accounted for
				#to test put print(s[2],s[3]) below the satellite loop for the real values and print the mag list in the elif statement
				mag.append(s[9])
				mag_err.append(s[10])
				zp.append(s[7])
				zp_err.append(s[8])
				obs_time.append(dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f'))
				filterband.append(s[3])
				RA.append(s[4])
				Dec.append(s[5])
				RA_pred.append(s[13]/15)
				Dec_pred.append(s[14])
				filename.append(s[12])
				if s[6] == None:
					elongation_list.append(np.nan)
				else:
					elongation_list.append(s[6])
				

	for i,filterindex in enumerate(filterband):
		if filterband!=[] and filterindex =='J':
			with open('D:\\UKRIT_2021\\_Output\\'+noradname+'_Filter_' +filterindex+'_'+group_start_time.strftime('%Y-%m-%d_%H-%M-%S')+ '.txt', "a") as file:
				file.write('%5s   %20s   %30s   %5s   %10.5f   %10.5f   %10.3f   %10.3f   %7.2f   %7.2f   %7.2f   %7.2f   %7.2f\n' % (noradname,satname,obs_time[i],filterindex,RA[i],RA_pred[i],Dec[i],Dec_pred[i],elongation_list[i],zp[i],zp_err[i],mag[i],mag_err[i]))
			file.close()
	nights = nights+1
	
	if s[0]==satellite:
		print("{} {} has been observed on {} nights.".format(noradname,satname,nights))
	#print("{} ".format(noradname))
	filterband,obs_time,elongation_list,mag,mag_err,zp,zp_err,RA,Dec,filename,RA_pred,Dec_pred = [],[],[],[],[],[],[],[],[],[],[],[]

	index = 0
	nights = 0

if plotlist:
	for i in range(len(plotlist)):
		if plotlist[i] not in found_sats:
			print('{} has no output because it was either not in the database or all of its images were rejected.'.format(plotlist[i]))
# Commit changes to database and close
print('Total Number of Nights of Observing in this aggregated data: {}.'.format(total_nights))
print('Total Number of Observations in this period: {}.'.format(totalobs))
conn.commit()
conn.close()
