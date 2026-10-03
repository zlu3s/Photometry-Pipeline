# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 09:44:16 2021

@author: ablock
"""

#!python
#
#Usage:
#Scans a directory to find Dark frames (CDS ReadMode)
#Takes median of darks to create a master dark
#Header information from a example dark is used to populate the new MaserDark
#Dark frame is written to the Master Darks directory

from tqdm import tqdm
from astropy.io import fits
import sys
import os
import numpy as  np
import shutil

filekey ='y'   #the starting string common to the data file names
endkey = '.fits'
dark_masters_directory = '/mnt/d/UKRIT_2021/Masters/Darks/'
search_num = 200

def Create_Master_Dark(DarksList,Darks_Data_Stack,directory):
	
	exemplar_hdul = fits.open(DarksList[0])
	exemplar_dark = exemplar_hdul[0].header
	exposure_time = (exemplar_dark['EXP_TIME'])
	#print('OK, found {} dark frames that are {} second exposures.'.format(len(DarksList),exposure_time))
	#print('Taking the median of the data to create the Master Dark frame...')
	master_dark = np.median(Darks_Data_Stack,axis=0)
	std = np.std(master_dark)
	mean = np.mean(master_dark)
	median = np.median(master_dark)
	variance = np.var(master_dark)
	#print('Copying some information from the Fits header of the first dark frame.')
	darkhead = fits.Header()
	darkhead['IMAGETYP'] = 'Master Dark'
	darkhead['OBSTYPE'] = 'DARK'
	darkhead['DATE-OBS'] = exemplar_dark['DATE-OBS']
	darkhead['EXP_TIME'] = exemplar_dark['EXP_TIME']
	darkhead['FILTER'] = exemplar_dark['FILTER']
	darkhead['GAIN'] = exemplar_dark['GAIN']
	darkhead['INSTRUME'] = exemplar_dark['INSTRUME']
	darkhead['TELESCOP'] = exemplar_dark['TELESCOP']
	darkhead['CAMNUM'] = exemplar_dark['CAMNUM']
	darkhead['MEAN'] = (mean, 'mean')
	darkhead['MEDIAN'] = (median, 'median')
	darkhead['STD'] = (std, 'standard dev')
	darkhead['VAR'] = (variance, 'variance')
	darkhead['NAXIS'] = 2
	darkhead['NAXIS1'] = master_dark.shape[0]
	darkhead['NAXIS2'] = master_dark.shape[1]
	masterdarkfits = fits.PrimaryHDU(master_dark, header=darkhead)

	masterdarkname = DarksList[0].split('_')
	masterdarkname = masterdarkname[0].split('y')
	masterdarkname = 'Dark Master_'+ masterdarkname[1]+'_'+str(exposure_time)+'sec.fits'
	#print('Saving master Dark ----> {}\n\n'.format(dark_masters_directory+ masterdarkname))
	masterdarkfits.writeto(masterdarkname, overwrite=True)
	shutil.copyfile(os.path.join(directory, os.fsencode(masterdarkname)), os.path.join(os.fsencode(dark_masters_directory), os.fsencode(masterdarkname)))

	
	return

def main():


	cwd = os.getcwd()
	#Set directory variable to be the type (bytes) read by os system 
	directory = os.fsencode(cwd)
	#change working directory
	os.chdir(directory)
	#FileList stores the Entire contents of directory- FitsList will be the data files
	FileList,FitsList,Darks_Data_Stack_20,Darks_Data_Stack_10,Darks_Data_Stack_5,Darks_Data_Stack_3,Darks_Data_Stack_2,Darks_Data_Stack_1,Darks_Data_Stack_1001,Darks_Data_Stack_15001= [],[],[],[],[],[],[],[],[],[]
	DarksList_20,DarksList_10,DarksList_5,DarksList_3,DarksList_2,DarksList_1,DarksList_1001,DarksList_15001 = [],[],[],[],[],[],[],[]

	#create FileList and a list of Fits files
	for file in os.listdir(directory):
			filename = os.fsdecode(file)
			FileList.append(filename)
			if filename.startswith(filekey) and filename.endswith(endkey):
				FitsList.append(filename)
	if not FitsList:
		sys.exit("No files found in this directory that match your command line file listing. The file list is empty.")
		
	print('There are {} files to check for darks in {}.'.format(len(FitsList),(cwd)))
	print('In this version of script, we are only going to examine the first {} files.'.format(search_num))
	FitsList.sort()	
	num=min(search_num, len(FitsList))
	for i in tqdm(range(num), desc="Progress"):
		hdul = fits.open(FitsList[i])
		hdr = hdul[0].header
		data = hdul[0].data
		data.astype(np.float32)
		if hdr['OBSTYPE'].strip()=='DARK' and hdr['EXP_TIME']== 20 and hdr['READOUT']=='NDR' and hdr['NEXP']== 1: 
			DarksList_20.append(FitsList[i])
			Darks_Data_Stack_20.append(data)
		if hdr['OBSTYPE'].strip()=='DARK' and hdr['EXP_TIME']== 10 and hdr['READOUT']=='CDS' and hdr['NEXP']== 1: 
			DarksList_10.append(FitsList[i])
			Darks_Data_Stack_10.append(data)
		if hdr['OBSTYPE'].strip()=='DARK' and hdr['EXP_TIME']== 5 and hdr['READOUT']=='CDS' and hdr['NEXP']== 1: 
			DarksList_5.append(FitsList[i])
			Darks_Data_Stack_5.append(data)
		if hdr['OBSTYPE'].strip()=='DARK' and hdr['EXP_TIME']== 3 and hdr['READOUT']=='CDS' and hdr['NEXP']== 1: 
			DarksList_3.append(FitsList[i])
			Darks_Data_Stack_3.append(data)
		if hdr['OBSTYPE'].strip()=='DARK' and hdr['EXP_TIME']== 2 and hdr['READOUT']=='CDS' and hdr['NEXP']== 1: 
			DarksList_2.append(FitsList[i])
			Darks_Data_Stack_2.append(data)
		if hdr['OBSTYPE'].strip()=='DARK' and hdr['EXP_TIME']== 1 and hdr['READOUT']=='CDS' and hdr['NEXP']== 1: 
			DarksList_1.append(FitsList[i])
			Darks_Data_Stack_1.append(data)
		if hdr['OBSTYPE'].strip() =='DARK' and hdr['EXP_TIME'] == 1.001 and hdr['READOUT'] =='CDS' and hdr['NEXP'] == 2: 
			DarksList_1001.append(FitsList[i])
			Darks_Data_Stack_1001.append(data)
		if hdr['OBSTYPE'].strip() =='DARK' and hdr['EXP_TIME'] == 15.001 and hdr['READOUT'] =='NDR' and hdr['NEXP'] == 2: 
			DarksList_15001.append(FitsList[i])
			Darks_Data_Stack_15001.append(data)
		hdul.close()	
	if DarksList_20:
		print('Creating 20 second (NDR) Master Dark from these frames:')
		print(DarksList_20)
		Create_Master_Dark(DarksList_20,Darks_Data_Stack_20,directory)
	if DarksList_10:
		print('Creating 10 second Master Dark from these frames:')
		print(DarksList_10)
		Create_Master_Dark(DarksList_10,Darks_Data_Stack_10,directory)
	if DarksList_5:
		print('Creating 5 second Master Dark from these frames:')
		print(DarksList_5)
		Create_Master_Dark(DarksList_5,Darks_Data_Stack_5,directory)
	if DarksList_3:
		print('Creating 3 second Master Dark from these frames:')
		print(DarksList_3)
		Create_Master_Dark(DarksList_3,Darks_Data_Stack_3,directory)
	if DarksList_2:
		print('Creating 2 second Master Dark from these frames:')
		print(DarksList_2)
		Create_Master_Dark(DarksList_2,Darks_Data_Stack_2,directory)
	if DarksList_1:
		print('Creating 1 second Master Dark from these frames:')
		print(DarksList_1)
		Create_Master_Dark(DarksList_1,Darks_Data_Stack_1,directory)
	if DarksList_1001:
		print('Creating 1 second Master Dark from these frames:')
		print('These are from 2 x 1sec coadded frames')
		print(DarksList_1001)
		Create_Master_Dark(DarksList_1001,Darks_Data_Stack_1001,directory)
	if DarksList_15001:
		print('Creating 15 second Master Dark from these frames:')
		print('These are from 2 x 15sec coadded frames')
		print(DarksList_15001)
		Create_Master_Dark(DarksList_15001,Darks_Data_Stack_15001,directory)
	
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
	main()
