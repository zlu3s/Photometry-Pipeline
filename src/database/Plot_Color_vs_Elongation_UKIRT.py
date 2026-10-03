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
import numpy as np



databaseFile = "D:\\UKRIT_2021\\Database\\ukirt.db"
index = 0
magnitude,phase_angle,colors = [],[],[]
sat_name,norad=[],[]
plotlist =[15039,22446,11141,11054]

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
#cursor.execute( "SELECT norad_id, name FROM sats WHERE type LIKE 'BREEZE%';" )
cursor.execute( "SELECT norad_id, name FROM sats;" )
for s in cursor:
	if plotlist:
		if s[0] in plotlist:
			sat_name.append(s[1])
			norad.append(s[0])
	else:
		sat_name.append(s[1])
		norad.append(s[0])
	
	
plotlist = norad

for i in range(len(norad)):
	magnitude,phase_angle,colors = [],[],[]
	select_string_statement="""SELECT sats.norad_id, images.filter, images.start_time, targets.magnitude, targets.sun_elong_predicted,targets.pp_aperture,targets.zeropoint,targets.fwhm,images.pp_aperture,targets.magnitude,targets.sextractor
				FROM ((sats INNER JOIN targets ON sats.id = targets.target_id) INNER JOIN images ON targets.image_id = images.id)
				WHERE (sats.norad_id = """+str(norad[i])+"""
					  AND targets.rejected < 1 
					  AND targets.inst_mag IS NOT NULL
					  AND targets.sextractor = 0
					  );"""

	# Print select items from combination of sats and targets and images tables
	cursor.execute(select_string_statement)
	for s in cursor:
		index=index+1
		#print(s[0],s[2],s[1],s[3],s[4],s[5],s[6],s[7],s[8],s[9],s[10])
		phase_angle.append(s[4])
		magnitude.append(s[3])
		colors.append(Colorize(s[1]))



	median_mag = np.median(np.array(magnitude))
	if ~(np.isnan (median_mag)):
		fig, (ax1) = plt.subplots(figsize=(12,6))
		fig.suptitle('Satellite '+str(norad[i])+' '+sat_name[i], size=25)
		print('Creating plot for {}'.format(str(norad[i])+' '+sat_name[i]))
		ax1.set_ylabel('Magnitude',size=20)
		ax1.set_xlabel('Elongation (degrees)', size = 20)
		ax1.grid(True)
		ax1.scatter(phase_angle,magnitude,color=colors,s = 1)
		ax1.set_ylim([median_mag+3, median_mag-4])
		ax1.set_xlim([50,180])
		zband = mpatches.Patch(color='blue', label='Z',linewidth=.5)
		yband = mpatches.Patch(color='gold', label='Y',linewidth=.5)
		jband = mpatches.Patch(color='#66AABB', label='J',linewidth=.5)
		hband = mpatches.Patch(color='crimson', label='H',linewidth=.5)
		kband = mpatches.Patch(color='purple', label='K',linewidth=.5)
		
		plt.rcParams["legend.fontsize"] = 12
		ax1.legend(handles=[zband,yband,jband,hband,kband])
		plt.savefig('D:\\UKRIT_2021\\xx_PLOTS_xx\\'+str(norad[i])+'__.png')
		plt.close('all')



# Commit changes to database and close
conn.commit()
conn.close()
