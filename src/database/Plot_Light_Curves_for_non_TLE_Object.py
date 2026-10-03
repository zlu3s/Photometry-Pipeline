# databaseAccessExample.py
#
# Example access script for SQLite database
# 
# More resources:
# https://www.tutorialspoint.com/sqlite/sqlite_python.htm
# https://www.w3schools.com/sql/
# 



import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import numpy as np
import datetime as dt




databaseFile = "D:\\UKRIT_2021\\Database\\ukirt.db"
grouping_time = 1250
plotlist = [39479]
#plotlist = [26738,32479,33491,33598,37381,37807,37952,38868,39376,39488,39614,39729,40259,40346,40385,42909,42433,43868,44458,47242,33059,33521,40101,40278,40355,40896,41840,43282,43447,43515,44911]
index = 0
sat_name,norad=[],[]
filterband,mag,magnitude_error,obs_time,elongation_list = [],[],[],[],[]
visits = 0
found_sats = []
totalobs=0
generate_plots = True



#not currently used, but will perhaps be later
def Colorize(filterband):
	
	color = ''
	
	if filterband == 'Z':
		color = 'blue'
	elif filterband == 'Y':
		color = 'gold'
	elif filterband == 'J':
		color = '#66AABB'
	elif filterband == 'H':
		color = 'crimson'
	elif filterband == 'K':
		color = 'purple'

	return(color)


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
cursor.execute("SELECT norad_id, name FROM sats")
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type LIKE 'HS-376%';" )
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type LIKE '%RB%';" )
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type  NOT LIKE 'HS-376%';" )
#cursor.execute( "SELECT norad_id, name FROM sats WHERE name LIKE '%Glonass%';" )
for s in cursor:
	if plotlist:
		if s[0] in plotlist:
			sat_name.append(s[1])
			print(sat_name)
			norad.append(s[0])
	else:
		sat_name.append(s[1])
		norad.append(s[0])
		


#AND images.start_time > strftime('%Y-%m-%d:%s','2024-12-01')
for satdex,satellite in enumerate(norad):
	select_string_statement="""SELECT sats.norad_id, images.filter, images.start_time, targets.magnitude, targets.sun_elong_predicted,sats.name,targets.sextractor
				FROM ((sats INNER JOIN targets ON sats.id = targets.target_id) INNER JOIN images ON targets.image_id = images.id)
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
			print(s[0],s[1],s[2],s[3],s[4],s[6])
			if index == 0: #initialize first time
				satname = s[5]
				noradname = str(s[0])
				found_sats.append(int(noradname))
				group_start_time = dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f')
			current_time = dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f')
			timedifference = (current_time - group_start_time).total_seconds()
			if timedifference >= 0 and timedifference < grouping_time: #finding >= zero was subtle
				#make lists of filter, magnitude, elongation and time
				filterband.append(Colorize(s[1]))
				mag.append(s[3])
				#print(current_time,timedifference,s[1],s[3],s[6])
				obs_time.append(dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f'))
				#print(noradname,s[1],round(s[4]),s[3])
				if s[4] == None:
					elongation_list.append(110) #since not known
				else:
					elongation_list.append(s[4])  #also record elongation
				index = index + 1
			elif timedifference > grouping_time and elongation_list:
				if ~(np.isnan((np.nanmean(np.array(elongation_list))))):
					if generate_plots:
						fig, (ax1) = plt.subplots(figsize=(12,6))
						fig.suptitle('GAIA Observatory', size=20)
						ax1.set_ylabel('Mag',size=20)
						ax1.set_xlabel('Observation Time (UTC)  '+ group_start_time.strftime('%Y-%m-%d'), size = 20)
						ax1.grid(False)
						myFmt = mdates.DateFormatter('%H:%M')
						plt.gca().xaxis.set_major_formatter(myFmt)
						ax1.scatter(obs_time,mag,color=filterband,s = 12)
						ax1.set_ylim([np.median(np.array(mag)) + 3, np.median(np.array(mag)) - 3])
						#ax1.set_ylim([14, 7])
						j = mpatches.Patch(color=Colorize('J'), label='J',linewidth=.5)
						y = mpatches.Patch(color=Colorize('Y'), label='Y',linewidth=.5)
						h= mpatches.Patch(color=Colorize('H'), label='H',linewidth=.5)
						k = mpatches.Patch(color=Colorize('K'), label='K',linewidth=.5)
						z = mpatches.Patch(color=Colorize('Z'), label='Z',linewidth=.5)
						
						
						plt.rcParams["legend.fontsize"] = 12
						ax1.legend(handles=[j,y,h,k,z])
						plt.savefig('D:\\UKRIT_2021\\xx_PLOTS_xx\\'+noradname+'_elong_' + str(round(np.nanmean(np.array(elongation_list))))+' '+group_start_time.strftime('%Y-%m-%d_%H-%M-%S')+ '_lightcurve.png')
					visits = visits +1
					
				filterband,mag,obs_time,elongation_list = [],[],[],[]
				group_start_time = current_time  #reset the group start time so that there so no observations are missed
				index = 0
				
				#Due to the way this is counted, the current value of s[3] would have been skipped. By appending it and
				#the other related bits of information everything should be accounted for
				#to test put print(s[2],s[3]) below the satellite loop for the real values and print the mag list in the elif statement
				mag.append(s[3])
				obs_time.append(dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f'))
				filterband.append(Colorize(s[1]))
				
				plt.close('all')
	if s[0] == satellite and  ~(np.isnan((np.nanmean(np.array(elongation_list))))):	
		elongation = ((np.nanmean(np.array(elongation_list))))

		if generate_plots:
			fig, (ax1) = plt.subplots(figsize=(12,6))
			fig.suptitle('GAIA Observatory', size=20)
			ax1.set_ylabel('Mag',size=20)
			ax1.set_xlabel('Observation Time (UTC)  '+ group_start_time.strftime('%Y-%m-%d'), size = 20)
			ax1.grid(False)
			myFmt = mdates.DateFormatter('%H:%M')
			plt.gca().xaxis.set_major_formatter(myFmt)
			ax1.scatter(obs_time,mag,color=filterband,s = 12)
			ax1.set_ylim([np.median(np.array(mag)) + 3, np.median(np.array(mag)) - 3])
			#ax1.set_ylim([22, 5])
			j = mpatches.Patch(color=Colorize('J'), label='J',linewidth=.5)
			y = mpatches.Patch(color=Colorize('Y'), label='Y',linewidth=.5)
			h= mpatches.Patch(color=Colorize('H'), label='H',linewidth=.5)
			k = mpatches.Patch(color=Colorize('K'), label='K',linewidth=.5)
			z = mpatches.Patch(color=Colorize('Z'), label='Z',linewidth=.5)
			plt.rcParams["legend.fontsize"] = 12
			ax1.legend(handles=[j,y,h,k,z])
			plt.savefig('D:\\UKRIT_2021\\xx_PLOTS_xx\\'+noradname+'_elong_' + str(round(elongation))+'_'+group_start_time.strftime('%Y-%m-%d_%H-%M-%S')+ '_lightcurve.png')
		visits = visits+1
		
		print("{} {} has been observed {} times.".format(noradname,satname,visits))
		#print("{} ".format(noradname))
		filterband,mag,obs_time,elongation_list = [],[],[],[]
		
		index = 0
		visits = 0
		plt.close('all')
if plotlist:
	for i in range(len(plotlist)):
		if plotlist[i] not in found_sats:
			print('{} has no output because it was either not in the database or all of its images were rejected.'.format(plotlist[i]))
# Commit changes to database and close
print('Total Number of Observations in this period: {}.'.format(totalobs))
conn.commit()
conn.close()

