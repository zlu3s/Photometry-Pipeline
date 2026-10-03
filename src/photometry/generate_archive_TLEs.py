# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 16:37:01 2021

@author: ngc1535
"""

from tqdm import tqdm
from astropy.io import fits
import sys
import os
import numpy as np
from spacetrack import SpaceTrackClient
import spacetrack.operators as op
import datetime as dt
import bisect
import time
from Satellite_Functions import *
from locations import *
from skyfield.api import utc
from Bounding_TLEs import *
from satellite_types import *
import matplotlib.pyplot as plt
import argparse
import datetime as dt

filekey ='y'   #the starting string common to the data file names
endkey = '.fits'

#account credentials at SpaceTrack.org
st = SpaceTrackClient('ngc1535@caelumobservatory.com','Supernovaof1054ad!')


def get_unique_MSBTITLE(fits_files):
	msbtitle_set = set()

	for fits_file in fits_files:
		with fits.open(fits_file) as hdul:
			hdr_ = hdul[0].header
			msbtitle = hdul[0].header.get('MSBTITLE')
			if msbtitle is not None and hdr_['RECIPE'].strip()=='MOVING_JITTER' and hdr_['OBSTYPE']=='OBJECT':
				msbtitle_set.add(msbtitle)

	return list(msbtitle_set)


def main():


	#Creation of the command line options and arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('Data_directory', help = 'Directory of Data (FITs Header) files. This is RawImages.')
	parser.add_argument('TLE_directory', help = 'TLE Archive Directory.')
	
	args = parser.parse_args()
	
	Data_path =  args.Data_directory
	#print(Data_path)
	TLE_path = args.TLE_directory #includes file name!
	FitsList= []
	notfoundintypelist = 0

	
	
	
	for dirs, subFolder, files in os.walk(Data_path):
		for filename in files:
			if filename.startswith(filekey) and filename.endswith(endkey):
				fileNameData_path = str(dirs)+'/'+str(filename)
				FitsList.append(fileNameData_path)
	if not FitsList:
		sys.exit("No files found in this directory that match your command line file listing. The file list is empty.")
		
		
	sat_count = 0
	index = 0
	filter_flag = False
	#previous_filter = 'Z'	
	#previous_target ='Something'
				
	for i in tqdm(range(len(FitsList)), desc='Progress'):
		notfoundintypelist = 0
		hdul = fits.open(FitsList[i])
		hdr = hdul[0].header
		#print(FitsList[i])
		if index == 0:
			counting_from_this_time = dt.datetime.strptime(hdr['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
			sat_ID_prime = hdr['MSBTITLE'].strip()
		current_time = dt.datetime.strptime(hdr['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
		timedifference = (current_time -counting_from_this_time).total_seconds()
		if hdr['RECIPE'].strip()=='MOVING_JITTER' and not filter_flag and hdr['MSBTITLE'].find('Sidereal')==-1 and hdr['OBSTYPE']=='OBJECT' and hdr['MSBTITLE'].find('TEST')==-1 and hdr['MSBTITLE']:
			sat_id = int(hdr['MSBTITLE'].strip())
			sat_historic_date = hdr['DATE-OBS'].replace('T',' ')
			split_fracSeconds = sat_historic_date.split('.')
			sat_historic_date = split_fracSeconds[0]
			if timedifference > 3600 or sat_ID_prime != sat_id or index == 0:
				counting_from_this_time = current_time
				sat_ID_prime = sat_id
				index = 1
				sat_count = sat_count +1
				if sat_count % 30 == 0:
					print("Sleeping for 60 seconds so as to not upset SpaceTrack.")
					time.sleep(60)
				TLE_RESULTS = (Bounding_TLEs(abs(sat_id),10,sat_historic_date))
				if TLE_RESULTS[2] == 0:
					closest_tle = TLE_RESULTS[0]
				else:
					closest_tle = TLE_RESULTS[1]
				sat_time = dt.datetime.strptime(sat_historic_date, '%Y-%m-%d %H:%M:%S') 
				sat_time = sat_time.replace(tzinfo=utc) 
				if not (TLE_RESULTS ==  ("None\nNone", "None\nNone",0)):
					sat_params = computeEphemeris(splitTLE(closest_tle),locations['UKIRT'],sat_time)
					with open(TLE_path, 'a') as f:
						f.write('Satellite ID: '+ str(sat_id)+'\n')
						f.write('Type: vestigial- not checking \n')
						f.write('DATE-OBS: '+ sat_historic_date+'\n')
						f.write('Prior TLE:\n')
						f.write(TLE_RESULTS[0]+'\n')
						f.write('Post TLE:\n')
						f.write(TLE_RESULTS[1]+'\n')
						f.write('TLE closest to observation time:\n')
						f.write(closest_tle+'\n')
						f.write('The rate of motion for this observation is: '+str(sat_params['velocity']*3600)+' arcseconds/sec.\n')
						f.write('Solar Elongation: '+str(sat_params['sunElong'])+'\n')
						f.write('--------------------------------------------------------------------------------\n')
						f.close()	
					#print(closest_tle)
					#print('Based on the closest TLE to your observation time, satellite {} is moving {:.2f} acrsec/sec\n\n'.format(sat_id,sat_params['velocity']*3600))
				
				if TLE_RESULTS == ("None\nNone", "None\nNone",0):
					with open(TLE_path, 'a') as f:
						f.write('Satellite ID: '+ str(sat_id)+'\n')
						f.write('Type: vestigial- not checking \n')
						f.write('DATE-OBS: '+ sat_historic_date+'\n')
						f.write('Prior TLE:\n')
						f.write(TLE_RESULTS[0]+'\n')
						f.write('Post TLE:\n')
						f.write(TLE_RESULTS[1]+'\n')
						f.write('TLE closest to observation time:\n')
						f.write(closest_tle+'\n')
						f.write('The rate of motion for this observation is: unknown.\n')
						f.write('Solar Elongation: unknown.\n')
						f.write('--------------------------------------------------------------------------------\n')
						f.close()
				else:
					notfoundintypelist += 1

		if notfoundintypelist < 0:
			print('\n\n\n!!!!!!!!!!!!!')
			print('Satellite {} is not found. Check the constraints statement.'.format(str(sat_id)))
			print('!!!!!!!!!!!!!\n\n\n')			
		#if hdr['FILTER'] == previous_filter:
			#filter_flag = True
		#if hdr['FILTER'] != previous_filter or (hdr['MSBTITLE'] != previous_target and hdr['MSBTITLE'].find('Sidereal')==-1):
			#filter_flag = False
		#print(hdr['FILTER'],previous_filter,hdr['MSBTITLE'],previous_target)
		#previous_filter = hdr['FILTER']
		#previous_target = hdr['MSBTITLE']
		hdul.close()
	


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
