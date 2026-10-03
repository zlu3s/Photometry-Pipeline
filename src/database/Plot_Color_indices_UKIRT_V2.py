# databaseAccessExample.py
#
# Example access script for SQLite database
# 
# More resources:
# https://www.tutorialspoint.com/sqlite/sqlite_python.htm
# https://www.w3schools.com/sql/
# 



import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import datetime as dt
import math
from matplotlib.patches import Circle
from itertools import combinations
from math import cos, sin, radians


cluster_shading = True
databaseFile = "D:\\UKRIT_2021\\Database\\ukirt.db"
sattype = '' #for select statement and  plot title
plotlist = [58204]
#plotlist = [26738,32479,33491,33598,37381,37807,37952,38868,39376,39488,39614,39729,40259,40346,40385,42909,42433,43868,44458,47242,33059,33521,40101,40278,40355,40896,41840,43282,43447,43515,44911]
#plotlist = [3431]
grouping_time = 1200
index = 0
group_start_time = 0
satname,noradname = '',''
magnitude,colors = [],[]
sat_name,norad=[],[]
jlist,klist,zlist,hlist,ylist = [],[],[],[],[] #temporary lists to hold magnitudes per satellite visit
jlist_err,klist_err,zlist_err,hlist_err,ylist_err=[],[],[],[],[] #list of errors for each magnitude above
jmean,kmean,zmean,hmean,ymean = [],[],[],[],[] #lists to hold mean values of magnitudes for each visit (from the lists above)
jtotal_err,ktotal_err,ztotal_err,htotal_err,ytotal_err = [],[],[],[],[] #lists to hold mean values of magnitude errors for each visit (from the lists above)
elongation_list,elongation_mean = [],[]        #elongation list and mean as the above
zminusy,yminusj,jminush,hminusk,jminusk = [],[],[],[],[]  #plotted values/color indices
zminusy_err,yminusj_err,jminush_err,hminusk_err,jminusk_err = [],[],[],[],[]
zyelong,yjelong,jhelong,hkelong,jkelong = [],[],[],[],[]  #Since some mean values may be empty (no observations), a matching elongation list is made for each color index
master_jminush, master_hminusk, master_yminusj,master_zminusy,master_satname,master_phase_angle,master_jminusk = [],[],[],[],[],[],[]
master_jminush_err, master_hminusk_err, master_yminusj_err,master_zminusy_err, master_jminusk_err,master_marker_track = [],[],[],[],[],[]
sattrack = []
time_track= []
marker_track =[]
marker_styles = ['o', 's','d','^', 'P', 'D', '*', 'X', 'h', 'v', '<', '>']

# Adam Graph Sizes
#size = [60, 40, 20, 60]
# Zeke Graph Sizes
size = [20, 15, 10, 30]


#created by a matplotlib developer in order to enable passing marker styles as a list into subplot scatter
#this is necessary in order to plot a different style marker for velocity
def mscatter(x,y,ax=None, m=None, **kw):
	import matplotlib.markers as mmarkers
	if not ax: ax=plt.gca()
	sc = ax.scatter(x,y,**kw)
	if (m is not None) and (len(m)==len(x)):
		paths = []
		for marker in m:
			if isinstance(marker, mmarkers.MarkerStyle):
				marker_obj = marker
			else:
				marker_obj = mmarkers.MarkerStyle(marker)
			path = marker_obj.get_path().transformed(marker_obj.get_transform())
			paths.append(path)
		sc.set_paths(paths)
	return sc

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


def Cluster_graphics(xcoords, ycoords, satgroup, ax=None):
    """
    Adds clustered data and center of mass circles to an existing plot.
    
    Parameters:
    - xcoords: List of x-coordinates.
    - ycoords: List of y-coordinates.
    - satgroup: List of group identifiers for each point.
    - ax: Matplotlib Axes object to which the points and circles will be added.
          If None, the function will create a new plot.
    """
    # Initialize an empty dictionary to store grouped data
    grouped_data = {}
    cluster_centers = {}
        
    # Group data by identifier, skipping NaN values
    for x, y, ident in zip(xcoords, ycoords, satgroup):
        if not (np.isnan(x) or np.isnan(y)):  # Skip if either coordinate is NaN
            if ident not in grouped_data:
                grouped_data[ident] = []
            grouped_data[ident].append((x, y))
        
    # Use a colormap for unique colors
    colormap = matplotlib.cm.get_cmap('tab10')   # Choose a colormap
    colors = {ident: colormap(i / len(grouped_data)) for i, ident in enumerate(grouped_data)}

    # Process each group for plotting
    for ident, coordinates in grouped_data.items():
        # Extract x and y coordinates
        x_coords, y_coords = zip(*coordinates)

        # Initial calculation of center of mass
        center_x = np.nanmean(x_coords)
        center_y = np.nanmean(y_coords)

        # Calculate distances from the initial center of mass
        distances = np.sqrt((np.array(x_coords) - center_x)**2 + (np.array(y_coords) - center_y)**2)

        # Find the cutoff distance for the desired percentile
        percentile_cutoff = np.percentile(distances, 80)

        # Identify the points within this percentile
        filtered_points = [(x, y) for x, y, d in zip(x_coords, y_coords, distances) if d <= percentile_cutoff]

        # If there are not enough points, skip to avoid errors
        if len(filtered_points) < 2:
            print(f"Not enough points in Group {ident} after filtering for percentile.")
            continue

        # Recalculate the center of mass for the filtered points
        filtered_x_coords, filtered_y_coords = zip(*filtered_points)
        center_x = np.mean(filtered_x_coords)
        center_y = np.mean(filtered_y_coords)
        
        # Recalculate the center of mass for the filtered points
        filtered_x_coords, filtered_y_coords = zip(*filtered_points)
        center_x = np.mean(filtered_x_coords)
        center_y = np.mean(filtered_y_coords)

        # Update the cluster_centers dictionary
        cluster_centers[ident] = (center_x, center_y)

        # Calculate the new distances from the refined center
        distances = np.sqrt((np.array(filtered_x_coords) - center_x)**2 + (np.array(filtered_y_coords) - center_y)**2)


        # Calculate the new distances from the refined center
        distances = np.sqrt((np.array(filtered_x_coords) - center_x)**2 + (np.array(filtered_y_coords) - center_y)**2)

        # Use the percentile to define the radius
        radius = np.percentile(distances, 90)

        # Plot the center of mass
        #ax.scatter(center_x, center_y, color='red', s=200, edgecolor='black', label=f'Center {ident}')

        # Add a shaded circle for the cluster
        circle = Circle((center_x, center_y), radius, color=colors[ident], alpha=0.05)
        ax.add_patch(circle)
        # Add a thin black outline to the shaded circle
        circle_outline = Circle((center_x, center_y), radius, edgecolor='black', facecolor='none', linewidth=0.5)
        ax.add_patch(circle_outline)

        # Calculate label position at the periphery of the circle
        angle = 150  # Specified angle in degrees (up is 0, right is 90)
        angle_rad = np.radians(angle)  # Convert angle to radians
        label_x = center_x + radius * np.cos(angle_rad) * 1.1  # Slightly offset the label
        label_y = center_y + radius * np.sin(angle_rad) * 1.1

        # Add the label to the plot
        ax.text(label_x, label_y, ident, fontsize=size[1], ha='center', va='center', fontweight='bold')

    # Print distances between cluster centers
    print("Distances between cluster centers:")
    ref_ident = list(cluster_centers.keys())[0] if cluster_centers else None  # Reference cluster (first group)
    if ref_ident:
        ref_center = cluster_centers[ref_ident]
        print(f"Reference Group {ref_ident}: Center = ({ref_center[0]:.3f}, {ref_center[1]:.3f})")

        for ident, center in cluster_centers.items():
            if ident == ref_ident:
                distance = 0.0
            else:
                distance = np.sqrt((center[0] - ref_center[0])**2 + (center[1] - ref_center[1])**2)
                print(f"Group {ident}: Center = ({center[0]:.3f}, {center[1]:.3f}), Distance from {ref_ident} = {distance:.3f}")

    if len(cluster_centers) == 0:
        print("No valid cluster centers calculated.")
        return

    # Calculate pairwise distances between cluster centers
    max_distance = 0
    max_pair = None
    print("\nPairwise distances between cluster centers:")
    for (ident1, center1), (ident2, center2) in combinations(cluster_centers.items(), 2):
        distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        print(f"Distance between {ident1} and {ident2}: {distance:.3f}")
        if distance > max_distance:
            max_distance = distance
            max_pair = (ident1, ident2)

    # Print the pair with the largest separation
    if max_pair:
        print(f"\nThe largest separation is between {max_pair[0]} and {max_pair[1]}: {max_distance:.3f}")

    return ax


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
search_string = "SELECT norad_id, name FROM sats WHERE type LIKE ?;"
parameters = (sattype + '%',)
# Execute the query using a cursor
cursor.execute(search_string, parameters)

#search_string =("SELECT norad_id, name FROM sats WHERE type LIKE 'HS-376%';" )
#cursor.execute( search_string )
for s in cursor:
	if plotlist:
		if s[0] in plotlist:
			sat_name.append(s[1])
			norad.append(s[0])
	else:
		sat_name.append(s[1])
		norad.append(s[0])
	
	
plotlist = norad


#AND images.start_time > strftime('%Y-%m-%d:%s','2021-01-01')
for satdex,satellite in enumerate(plotlist):
	magnitude,phase_angle,colors = [],[],[]
	select_string_statement="""SELECT sats.norad_id, images.filter, images.start_time, targets.magnitude, targets.sun_elong_predicted,sats.name,targets.sextractor,targets.magnitude_error
				FROM ((sats INNER JOIN targets ON sats.id = targets.target_id) INNER JOIN images ON targets.image_id = images.id)
				WHERE (sats.norad_id = """+str(satellite)+"""
					  AND targets.rejected < 1 
					  AND targets.inst_mag IS NOT NULL
					  AND targets.sextractor = 0
					  )
				ORDER BY images.start_time;"""

	# Print select items from combination of sats and targets and images tables
	cursor.execute(select_string_statement)
	for s in cursor:
		if s[0] == satellite:
			if index == 0: #initialize first time
				satname = s[5]
				noradname = str(s[0])
				marker = marker_styles[satdex % len(marker_styles)]
				group_start_time = dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f') 
			current_time = dt.datetime.strptime(s[2], '%Y-%m-%d %H:%M:%S.%f')
			timedifference = (current_time - group_start_time).total_seconds()
			if timedifference >= 0 and timedifference < grouping_time: #finding >= zero was subtle
				#make lists of magnitudes in each band
				#the square  of the error is appended 
				if s[1] == "J":
					if s[3] and s[3] < 25:
						jlist.append(s[3])
						jlist_err.append(s[7]**2)
					else:
						jlist.append(np.nan)
						jlist_err.append(np.nan)
				if s[1] == "H" and s[3]:
					if s[3] and s[3] < 25:
						hlist.append(s[3])
						hlist_err.append(s[7]**2)
					else:
						hlist.append(np.nan)
						hlist_err.append(np.nan)
				if s[1] == "Y":
					if s[3] and s[3] < 25:
						ylist.append(s[3])
						ylist_err.append(s[7]**2)
					else:
						ylist.append(np.nan)
						ylist_err.append(np.nan)
				if s[1] == "K":
					if s[3] and s[3] < 25:
						klist.append(s[3])
						klist_err.append(s[7]**2)
					else:
						klist.append(np.nan)
						klist_err.append(np.nan)
				if s[1] == "Z":
					if s[3] and s[3] < 25:
						zlist.append(s[3])
						zlist_err.append(s[7]**2)
					else:
						zlist.append(np.nan)
						zlist_err.append(np.nan)
				if s[4]:
					elongation_list.append(s[4])  #also record elongation
				else:
					#elongation_list.append(np.nan)
					elongation_list.append(163) #insert a elongation if satellite has no TLE
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
					
				elongation_mean.append(np.median(np.array(elongation_list)))
				sattrack.append(noradname)
				marker_track.append(marker)
				
				

				
					
				#reset temporary lists
				jlist,klist,zlist,hlist,ylist,elongation_list = [],[],[],[],[],[]
				jlist_err,klist_err,zlist_err,hlist_err,ylist_err = [],[],[],[],[]
				
				#Regardless of condition, values are appended in each part of the IF/ELSE statement
				#These then are the first in the next grouping. There is probably a better way since this is in both. 
				#the square of the error is appended 
				if s[1] == "J":
					if s[3] and s[3] < 25:
						jlist.append(s[3])
						jlist_err.append(s[7]**2)
					else:
						jlist.append(np.nan)
						jlist_err.append(np.nan)
				if s[1] == "H":
					if s[3] and s[3] < 25:
						hlist.append(s[3])
						hlist_err.append(s[7]**2)
					else:
						hlist.append(np.nan)
						hlist_err.append(np.nan)
				if s[1] == "Y":
					if s[3] and s[3] < 25:
						ylist.append(s[3])
						ylist_err.append(s[7]**2)
					else:
						ylist.append(np.nan)
						ylist_err.append(np.nan)
				if s[1] == "K":
					if s[3] and s[3] < 25:
						klist.append(s[3])
						klist_err.append(s[7]**2)
					else:
						klist.append(np.nan)
						klist_err.append(np.nan)
				if s[1] == "Z":
					if s[3] and s[3] < 25:
						zlist.append(s[3])
						zlist_err.append(s[7]**2)
					else:
						zlist.append(np.nan)
						zlist_err.append(np.nan)
				if s[4]:
					elongation_list.append(s[4])  #also record elongation
				else:
					#elongation_list.append(np.nan)
					elongation_list.append(163) #insert a elongation if satellite has no TLE
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
		
	elongation_mean.append(np.nanmedian(np.array(elongation_list)))
	time_track.append(group_start_time)
	sattrack.append(noradname)
	marker_track.append(marker)
	
	

	
	print('++++++++++++++++++++++++++++')
	print(noradname,satname)
	print(' ')
	print('VISITS')
	print(len(elongation_mean))
	print('')

	
	#creating the points to plot. Checks if no value in either filter (skips if so)Thus the matching of elongation
	for i in range(len(elongation_mean)):
		if zmean[i] and ymean[i] and elongation_mean[i]:
			zminusy.append(zmean[i] - ymean[i])
			zminusy_err.append(math.sqrt((ztotal_err[i])**2+(ytotal_err[i])**2))
			zyelong.append(elongation_mean[i])
		else:
			zminusy.append(np.nan)
			zyelong.append(np.nan)
			zminusy_err.append(np.nan)
			
		if ymean[i] and jmean[i] and elongation_mean[i]:
			yminusj.append(ymean[i] - jmean[i])
			yminusj_err.append(math.sqrt((ytotal_err[i])**2+(jtotal_err[i])**2))
			yjelong.append(elongation_mean[i])
		else:
			yminusj.append(np.nan)
			yjelong.append(np.nan)
			yminusj_err.append(np.nan)
			
		if jmean[i] and hmean[i] and elongation_mean[i]:
			jminush.append(jmean[i] - hmean[i])
			jminush_err.append(math.sqrt((jtotal_err[i])**2+(htotal_err[i])**2))
			jhelong.append(elongation_mean[i])
		else:
			jminush.append(np.nan)
			jhelong.append(np.nan)
			jminush_err.append(np.nan)
			
		if hmean[i] and kmean[i] and elongation_mean[i]:
			hminusk.append(hmean[i] - kmean[i])
			hminusk_err.append(math.sqrt((htotal_err[i])**2+(ktotal_err[i])**2))
			hkelong.append(elongation_mean[i])
		else:
			hminusk.append(np.nan)
			hkelong.append(np.nan)
			hminusk_err.append(np.nan)
			
		if jmean[i] and kmean[i] and elongation_mean[i]:
			jminusk.append(jmean[i] - kmean[i])
			jminusk_err.append(math.sqrt((jtotal_err[i])**2+(ktotal_err[i])**2))
			jkelong.append(elongation_mean[i])
		else:
			jminusk.append(np.nan)
			jkelong.append(np.nan)
			jminusk_err.append(np.nan)
			
		print('For Elongation {:.0f} degrees on {}'.format(elongation_mean[i],time_track[i]))
		print('Color Indices are: Z-Y {:.3f}  Y-J {:.3f}  J-H {:.3f}  H-K {:.3f} J-K {:.3f}'.format(zminusy[i],yminusj[i],jminush[i],hminusk[i],jminusk[i]))
		print('Errors are: Z-Y {:.3f}  Y-J {:.3f}  J-H {:.3f}  H-K {:.3f} J-K {:.3f}\n'.format(zminusy_err[i],yminusj_err[i],jminush_err[i],hminusk_err[i],jminusk_err[i]))
		
	
		
	meanlist = jminush + hminusk + zminusy + yminusj +jminusk	
	if np.isnan(np.nanmedian(np.array(meanlist))):
		graphcenter = 0
	else:
		graphcenter = np.nanmedian(np.array(meanlist))
	
	fig, (ax1) = plt.subplots(figsize=(12,6))
	fig.suptitle('Satellite '+noradname+' '+satname, size=25)
	ax1.set_ylabel('Color Indices',size=20)
	ax1.set_xlabel('Elongation (degrees)', size = 20)
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
	#plt.savefig('W:\\Satellite_Programs\\'+noradname+'_indices.png')

	
	if ~(np.isnan(np.nanmedian(np.array(meanlist)))):
		master_satname.extend(sattrack)
		master_phase_angle.extend(elongation_mean) #to be converted to phase angle below
		master_jminush.extend(jminush)
		master_zminusy.extend(zminusy)
		master_yminusj.extend(yminusj)
		master_hminusk.extend(hminusk)
		master_jminusk.extend(jminusk)
		master_jminush_err.extend(jminush_err)
		master_zminusy_err.extend(zminusy_err)
		master_yminusj_err.extend(yminusj_err)
		master_hminusk_err.extend(hminusk_err)
		master_jminusk_err.extend(jminusk_err)
		master_marker_track.extend(marker_track)
	else:
		print('Satellite {} is being skipped.'.format(noradname+' '+satname))
	#print(len(master_satname),len(master_jminush),len(master_zminusy),len(master_yminusj),len(master_hminusk),len(master_phase_angle),len(master_hminusk),len(master_hminusk_err))
	print('\n++++++++++++++++++++++++++++')
	
	
	
	zmean,ymean,jmean,kmean,hmean,zminusy,yminusj,jminush,hminusk,jminusk,elongation_list,elongation_mean = [],[],[],[],[],[],[],[],[],[],[],[]
	jtotal_err,ktotal_err,ztotal_err,htotal_err,ytotal_err = [],[],[],[],[]
	zminusy_err,yminusj_err,jminush_err,hminusk_err,jminusk_err = [],[],[],[],[]
	jlist,klist,ylist,zlist,hlist = [],[],[],[],[]
	jlist_err,klist_err,zlist_err,hlist_err,ylist_err=[],[],[],[],[]
	zyelong,yjelong,jhelong,hkelong,jkelong = [],[],[],[],[]
	sattrack = []
	time_track = []
	marker_track=[]
	index = 0
	plt.close('all')

#convert elongation to phase_angle
for i in range(len(master_phase_angle)):
	master_phase_angle[i] = 180-master_phase_angle[i]
	


fig, (ax1) = plt.subplots(figsize=(12,6))
if len(plotlist)> 1:
	fig.suptitle('MORELOS 3', size=size[0])
else:
	fig.suptitle(sattype+noradname+' '+satname+'   ', size=size[0])
	#fig.suptitle(sattype+noradname+' '+'ELEKTRO L4'+'   ', size=size[0])
ax1.set_facecolor("#666666")
ax1.set_ylabel('H-K',size=size[1])
ax1.set_xlabel('J-H', size = size[1])
ax1.tick_params(axis='both', which='major', labelsize=size[2])
ax1.tick_params(axis='both', which='minor', labelsize=size[2])
ax1.grid(True)
colors = matplotlib.cm.get_cmap('RdYlBu_r')
levels,steps = np.linspace(0,180,180,retstep=True)
ticks = np.linspace(0,180,10)
cax =mscatter(
	master_jminush,
	master_hminusk,
	ax=ax1,
	s=size[3], #To Hide the points make this value "0"
	c=master_phase_angle,
	cmap=colors,  # The colormap is already applied here
	#edgecolor='face',  # Use the same color for edges as the mapped face color
	#facecolor='none',  # Unfilled markers
	m=master_marker_track
)
#ax1.errorbar(master_jminush,master_hminusk,xerr=master_jminush_err,yerr=master_hminusk_err,color="black",fmt='none')
ax1.set_xlim([-2,2])
ax1.set_ylim([-2,2])
cbar = plt.colorbar(cax, fraction=0.046, pad=0.04,aspect=50,shrink=0.8, ticks=ticks,format="%.2f")
cbar.set_label('Phase Angle (Degrees)',size = size[1])
cbar.ax.tick_params(labelsize=size[2])
# Add cluster graphics (centers of mass and circles) to the existing plot
if cluster_shading:
    Cluster_graphics(master_jminush,master_hminusk,master_satname,ax1)


#if len(plotlist)> 1:
	#for i in range(len(master_satname)):
		#ax1.annotate(master_satname[i],[master_jminush[i]+.003,master_hminusk[i]+.003])
	
	


plt.rcParams["legend.fontsize"] = 12
#plt.savefig('"W:\\Satellite_Programs\\hminuk_vs_jminush.png')


# Commit changes to database and close
conn.commit()
conn.close()
