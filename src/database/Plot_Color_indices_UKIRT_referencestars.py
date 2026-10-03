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
from matplotlib.offsetbox import AnchoredText
import numpy as np
import datetime as dt
import math



databaseFile = "D:\\UKRIT_2021\\Database\\ukirt.db"
sattype = '' #for select statement and  plot title
plotlist = ['99999 Sidereal']
grouping_time = 720
index = 0
magnitude,colors = [],[]
sat_name,norad=[],[]
jlist,klist,zlist,hlist,ylist = [],[],[],[],[] #temporary lists to hold magnitudes per satellite visit
jlist_err,klist_err,zlist_err,hlist_err,ylist_err=[],[],[],[],[] #list of errors for each magnitude above
jmean,kmean,zmean,hmean,ymean = [],[],[],[],[] #lists to hold mean values of magnitudes for each visit (from the lists above)
jtotal_err,ktotal_err,ztotal_err,htotal_err,ytotal_err = [],[],[],[],[] #lists to hold mean values of magnitude errors for each visit (from the lists above)
airmass_list,airmass_mean = [],[]        #airmass list and mean as the above
zminusy,yminusj,jminush,hminusk = [],[],[],[]  #plotted values/color indices
zminusy_err,yminusj_err,jminush_err,hminusk_err = [],[],[],[]
zyelong,yjelong,jhelong,hkelong = [],[],[],[]  #Since some mean values may be empty (no observations), a matching airmass list is made for each color index
master_jminush, master_hminusk, master_yminusj,master_zminusy,master_satname,master_phase_angle = [],[],[],[],[],[]
master_jminush_err, master_hminusk_err, master_yminusj_err,master_zminusy_err = [],[],[],[]
sattrack = []
time_track= []




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

#AND images.start_time > strftime('%Y-%m-%d:%s','2021-01-01')
for satdex,satellite in enumerate(plotlist):
	magnitude,phase_angle,colors = [],[],[]
	select_string_statement="""SELECT images.msb_title,images.filter,images.start_time,referenceStars.zeropoint,images.airmass,referenceStars.zeropoint_error
			FROM images INNER JOIN referenceStars ON images.id = referenceStars.image_id
			WHERE images.msb_title LIKE "%99999 Sidereal%" AND referenceStars.rejected = 0
			ORDER BY images.start_time;"""

	# Print select items from combination of sats and targets and images tables
	cursor.execute(select_string_statement)
	for s in cursor:
		if s[0]:
			if index == 0: #initialize first time
				satname = 'Standard Star Field #152 '
				noradname = 'Standard Star Field #152'
				group_start_time = dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f') 
			current_time = dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f')
			timedifference = (current_time - group_start_time).total_seconds()
			if timedifference >= 0 and timedifference < grouping_time: #finding >= zero was subtle
				#make lists of magnitudes in each band
				#the square  of the error is appended 
				if s[1] == "J":
					if s[3] and s[3]:
						jlist.append(s[3])
						jlist_err.append(s[5]**2)
					else:
						jlist.append(np.nan)
						jlist_err.append(np.nan)
				if s[1] == "H" and s[3]:
					if s[3] and s[3]:
						hlist.append(s[3])
						hlist_err.append(s[5]**2)
					else:
						hlist.append(np.nan)
						hlist_err.append(np.nan)
				if s[1] == "Y":
					if s[3] and s[3]:
						ylist.append(s[3])
						ylist_err.append(s[5]**2)
					else:
						ylist.append(np.nan)
						ylist_err.append(np.nan)
				if s[1] == "K":
					if s[3] and s[3]:
						klist.append(s[3])
						klist_err.append(s[5]**2)
					else:
						klist.append(np.nan)
						klist_err.append(np.nan)
				if s[1] == "Z":
					if s[3] and s[3]:
						zlist.append(s[3])
						zlist_err.append(s[5]**2)
					else:
						zlist.append(np.nan)
						zlist_err.append(np.nan)
				if s[4]:
					airmass_list.append(s[4])  #also record airmass
				else:
					airmass_list.append(np.nan)
			else:
				time_track.append(group_start_time)
				group_start_time = current_time  #reset the group start time so that there so no observations are missed
				#calculate mean values. If no values, append placeholder so all lists are the same length				
				#total error is the sqrt of the addition of the errors divided by N
				if jlist:	
					jmean.append(np.nanmedian(np.array(jlist)))
					jtotal_err.append( math.sqrt( np.sum(np.array(jlist_err))) / len(jlist_err))
				else:
					jmean.append([])
					jtotal_err.append([])
				if hlist  :	
					hmean.append(np.nanmedian(np.array(hlist)))
					htotal_err.append( math.sqrt( np.nansum(np.array(hlist_err))) / len(hlist_err))
				else:
					hmean.append([])
					htotal_err.append([])
				if ylist:	
					ymean.append(np.nanmedian(np.array(ylist)))	
					ytotal_err.append( math.sqrt( np.sum(np.array(ylist_err))) / len(ylist_err))
				else:
					ymean.append([])
					ytotal_err.append([])
				if klist:	
					kmean.append(np.nanmedian(np.array(klist)))
					ktotal_err.append( math.sqrt( np.nansum(np.array(klist_err))) / len(klist_err))
				else:
					kmean.append([])
					ktotal_err.append([])
				if zlist:	
					zmean.append(np.nanmedian(np.array(zlist)))
					ztotal_err.append( math.sqrt( np.sum(np.array(zlist_err))) / len(zlist_err))
				else:
					zmean.append([])
					ztotal_err.append([])
					
				airmass_mean.append(np.median(np.array(airmass_list)))
				sattrack.append(noradname)
				

				
					
				#reset temporary lists
				jlist,klist,zlist,hlist,ylist,airmass_list = [],[],[],[],[],[]
				jlist_err,klist_err,zlist_err,hlist_err,ylist_err = [],[],[],[],[]
				
				#Regardless of condition, values are appended in each part of the IF/ELSE statement
				#These then are the first in the next grouping. There is probably a better way since this is in both. 
				#the square of the error is appended 
				if s[1] == "J":
					if s[3] and s[3]:
						jlist.append(s[3])
						jlist_err.append(s[5]**2)
					else:
						jlist.append(np.nan)
						jlist_err.append(np.nan)
				if s[1] == "H":
					if s[3] and s[3]:
						hlist.append(s[3])
						hlist_err.append(s[5]**2)
					else:
						hlist.append(np.nan)
						hlist_err.append(np.nan)
				if s[1] == "Y":
					if s[3] and s[3]:
						ylist.append(s[3])
						ylist_err.append(s[5]**2)
					else:
						ylist.append(np.nan)
						ylist_err.append(np.nan)
				if s[1] == "K":
					if s[3] and s[3]:
						klist.append(s[3])
						klist_err.append(s[5]**2)
					else:
						klist.append(np.nan)
						klist_err.append(np.nan)
				if s[1] == "Z":
					if s[3] and s[3]:
						zlist.append(s[3])
						zlist_err.append(s[5]**2)
					else:
						zlist.append(np.nan)
						zlist_err.append(np.nan)
				if s[4]:
					airmass_list.append(s[4])  #also record airmass
				else:
					airmass_list.append(np.nan)
			#for bookeeping... but used at the moment
			index=index+1
	# the last bit of data after the last else statement (Enters if..but never gets to Else...so lists are not averaged)		
	if jlist:	
		jmean.append(np.median(np.array(jlist)))
		jtotal_err.append( math.sqrt( np.sum(np.array(jlist_err))) / len(jlist_err))
	else:
		jmean.append([])
		jtotal_err.append([])
	if hlist  :	
		hmean.append(np.nanmedian(np.array(hlist)))
		htotal_err.append( math.sqrt( np.nansum(np.array(hlist_err))) / len(hlist_err))
	else:
		hmean.append([])
		htotal_err.append([])
	if ylist:	
		ymean.append(np.nanmedian(np.array(ylist)))	
		ytotal_err.append( math.sqrt( np.sum(np.array(ylist_err))) / len(ylist_err))
	else:
		ymean.append([])
		ytotal_err.append([])
	if klist:	
		kmean.append(np.nanmedian(np.array(klist)))
		ktotal_err.append( math.sqrt( np.nansum(np.array(klist_err))) / len(klist_err))
	else:
		kmean.append([])
		ktotal_err.append([])
	if zlist:	
		zmean.append(np.nanmedian(np.array(zlist)))
		ztotal_err.append( math.sqrt( np.sum(np.array(zlist_err))) / len(zlist_err))
	else:
		zmean.append([])
		ztotal_err.append([])
		
	airmass_mean.append(np.nanmedian(np.array(airmass_list)))
	time_track.append(group_start_time)
	sattrack.append(noradname)
	

	
	print('++++++++++++++++++++++++++++')
	print(noradname,satname)
	print(' ')
	print('Number Standard Star Observations')
	print(len(airmass_mean))
	print('')

	
	#creating the points to plot. Checks if no value in either filter (skips if so)Thus the matching of airmass
	for i in range(len(airmass_mean)):
		if zmean[i] and ymean[i] and airmass_mean[i]:
			zminusy.append(zmean[i] - ymean[i])
			zminusy_err.append(math.sqrt((ztotal_err[i])**2+(ytotal_err[i])**2))
			zyelong.append(airmass_mean[i])
		else:
			zminusy.append(np.nan)
			zyelong.append(np.nan)
			zminusy_err.append(np.nan)
			
		if ymean[i] and jmean[i] and airmass_mean[i]:
			yminusj.append(ymean[i] - jmean[i])
			yminusj_err.append(math.sqrt((ytotal_err[i])**2+(jtotal_err[i])**2))
			yjelong.append(airmass_mean[i])
		else:
			yminusj.append(np.nan)
			yjelong.append(np.nan)
			yminusj_err.append(np.nan)
			
		if jmean[i] and hmean[i] and airmass_mean[i]:
			jminush.append(jmean[i] - hmean[i])
			jminush_err.append(math.sqrt((jtotal_err[i])**2+(htotal_err[i])**2))
			jhelong.append(airmass_mean[i])
		else:
			jminush.append(np.nan)
			jhelong.append(np.nan)
			jminush_err.append(np.nan)
			
		if hmean[i] and kmean[i] and airmass_mean[i]:
			hminusk.append(hmean[i] - kmean[i])
			hminusk_err.append(math.sqrt((htotal_err[i])**2+(ktotal_err[i])**2))
			hkelong.append(airmass_mean[i])
		else:
			hminusk.append(np.nan)
			hkelong.append(np.nan)
			hminusk_err.append(np.nan)
			
		print('For airmass of {:.2f} on {}'.format(airmass_mean[i],time_track[i]))
		print('Color Indices are: Z-Y {:.3f}  Y-J {:.3f}  J-H {:.3f}  H-K {:.3f}'.format(zminusy[i],yminusj[i],jminush[i],hminusk[i]))
		print('Errors are: Z-Y {:.3f}  Y-J {:.3f}  J-H {:.3f}  H-K {:.3f}\n'.format(zminusy_err[i],yminusj_err[i],jminush_err[i],hminusk_err[i]))
		
	
		
	meanlist = jminush + hminusk + zminusy + yminusj	
	if np.isnan(np.nanmedian(np.array(meanlist))):
		graphcenter = 0
	else:
		graphcenter = np.nanmedian(np.array(meanlist))
	
	fig, (ax1) = plt.subplots(figsize=(12,6))
	fig.suptitle('Satellite '+noradname+' '+satname, size=25)
	ax1.set_ylabel('Color Indices',size=20)
	ax1.set_xlabel('airmass (degrees)', size = 20)
	ax1.grid(True)
	ax1.scatter(zyelong,zminusy,color='blue',s = 12)
	ax1.scatter(yjelong,yminusj,color='gold',s = 12)
	ax1.scatter(jhelong,jminush,color='#66AABB',s = 12)
	ax1.scatter(hkelong,hminusk,color='crimson',s = 12)
	ax1.set_xlim([50,180])
	ax1.set_ylim([graphcenter - 1.5, graphcenter + 1.5])
	zy = mpatches.Patch(color='blue', label='Z-Y',linewidth=.5)
	yj = mpatches.Patch(color='gold', label='Y-J',linewidth=.5)
	jh= mpatches.Patch(color='#66AABB', label='J-H',linewidth=.5)
	hk = mpatches.Patch(color='crimson', label='H-K',linewidth=.5)
	
	
	plt.rcParams["legend.fontsize"] = 12
	ax1.legend(handles=[zy,yj,jh,hk])
	plt.savefig('D:\\UKRIT_2021\\xx_PLOTS_xx\\'+noradname+'_indices.png')
	
	if ~(np.isnan(np.nanmedian(np.array(meanlist)))):
		master_satname.extend(sattrack)
		master_phase_angle.extend(airmass_mean) 
		master_jminush.extend(jminush)
		master_zminusy.extend(zminusy)
		master_yminusj.extend(yminusj)
		master_hminusk.extend(hminusk)
		master_jminush_err.extend(jminush_err)
		master_zminusy_err.extend(zminusy_err)
		master_yminusj_err.extend(yminusj_err)
		master_hminusk_err.extend(hminusk_err)
	else:
		print('Satellite {} is being skipped.'.format(noradname+' '+satname))
	#print(len(master_satname),len(master_jminush),len(master_zminusy),len(master_yminusj),len(master_hminusk),len(master_phase_angle),len(master_hminusk),len(master_hminusk_err))
	print('\n++++++++++++++++++++++++++++')
	
	
	
	zmean,ymean,jmean,kmean,hmean,zminusy,yminusj,jminush,hminusk,airmass_list,airmass_mean = [],[],[],[],[],[],[],[],[],[],[]
	jtotal_err,ktotal_err,ztotal_err,htotal_err,ytotal_err = [],[],[],[],[]
	zminusy_err,yminusj_err,jminush_err,hminusk_err = [],[],[],[]
	jlist,klist,ylist,zlist,hlist = [],[],[],[],[]
	jlist_err,klist_err,zlist_err,hlist_err,ylist_err=[],[],[],[],[]
	zyelong,yjelong,jhelong,hkelong = [],[],[],[]
	sattrack, time_track = [],[]
	index = 0
	plt.close('all')


fig, (ax1) = plt.subplots(figsize=(12,6))
if len(plotlist)> 1:
	fig.suptitle(sattype+'   Satellite Color Clouds   ', size=25)
else:
	fig.suptitle(sattype+satname+'   ', size=25)
ax1.set_ylabel('H-K',size=20)
ax1.set_xlabel('J-H', size = 20)
ax1.grid(True)
colors = plt.cm.get_cmap('RdYlBu')
levels,steps = np.linspace(0,2,20,retstep=True)
ticks = np.linspace(0,2,10)
cax = ax1.scatter(master_jminush,master_hminusk,s=100,c = master_phase_angle,cmap=colors)
ax1.errorbar(master_jminush,master_hminusk,xerr=master_jminush_err,yerr=master_hminusk_err,color="black",fmt='none')
#ax1.set_xlim([-0.3,0.75])
#ax1.set_ylim([-0.75,0.75])
cbar = plt.colorbar(cax, fraction=0.046, pad=0.04,aspect=50,shrink=0.8, ticks=ticks)
cbar.set_label('Airmass',size = 20)

if len(plotlist)> 1:
	for i in range(len(master_satname)):
		ax1.annotate(master_satname[i],[master_jminush[i]+.003,master_hminusk[i]+.003])
	


plt.rcParams["legend.fontsize"] = 12
plt.savefig('D:\\UKRIT_2021\\xx_PLOTS_xx\\hminuk_vs_jminush.png')


Data= [x for x in master_hminusk if np.isnan(x) == False]
fig, (ax2) = plt.subplots(figsize=(10,10))
fig.suptitle('H-K Zeropoints')
ax2.set_ylabel('Frequency')


std = np.std(Data)
median = np.median(Data)
bins = np.linspace(median-4*std,median+4*std,50)

#bins = np.linspace(min(Data),max(Data),60)
n, bins, patches = ax2.hist(Data,bins,color ='darkred')
at = AnchoredText(
    'Std             '+str(round(std,2))+'\nMedian      '+str(round(median,2)), prop=dict(size=15), frameon=True, loc='upper left')
at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
ax2.add_artist(at)
	
plt.savefig('D:\\UKRIT_2021\\xx_PLOTS_xx\\hminusk_standardstars.png')
		


# Commit changes to database and close
conn.commit()
conn.close()
