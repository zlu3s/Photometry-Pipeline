
#!python
#
#Usage:
# by Adam Block


import sys
import os
import argparse
from tqdm import tqdm
import warnings
from astropy.io import fits


warnings.filterwarnings("ignore", category=UserWarning)
filekey ='y'   #the starting string common to the data file names
endkey = 'HEADER.fit'


def main():
	
	
	#Creation of the command line options and arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('Data_directory', help = 'Directory of Data (FITs Header) files. This is RawImages.')
	parser.add_argument('Output_directory', help = 'Where the output tex file goes..',action='store')

	
	args = parser.parse_args()

	
	path = args.Data_directory
	output_directory = args.Output_directory
	#FileList stores the Entire contents of directory- FitsList will be the data files
	FileList,FitsList = [],[]

	for dirs, subFolder, files in os.walk(path):
		for filename in files:
			if filename.startswith(filekey) and filename.endswith(endkey):
				fileNameData_path = str(dirs)+'/'+str(filename)
				FitsList.append(fileNameData_path)
	if not FitsList:
		sys.exit("No files found in this directory that match your command line file listing. The file list is empty.")



	with open(output_directory+"_UKIRT_header_scan.txt", "w") as file:
		file.write('{:<65} {:<10}{:<20}{:<10}{:<10}{:<10}{:<10}\n'.format('Filename','OBSTYPE','Target','Filter','EXP_TIME','Num Exp','Readout Mode'))
		for i in tqdm(range(len(FitsList)), desc=f"Scanning Progress"):
			hdul = fits.open(FitsList[i])
			hdr = hdul[0].header
			JRecipe = hdr['NJITTER']
			imagetype = hdr['OBSTYPE']
			exp_time = hdr['EXP_TIME']
			nexp = hdr['NEXP']
			if nexp == 2 and exp_time == 1:
				#fits.setval(FitsList[i], 'EXP_TIME', value='1.001',output_verify='ignore')
				hdr['EXP_TIME']= 1.001
				hdr.comments['EXP_TIME'] = 'A Mosiac of 2 x 1 second exposures'
				hdul.writeto(FitsList[i],output_verify='ignore',overwrite='True')
				exp_time = '1.001'
			if nexp == 2 and exp_time == 15:
				#fits.setval(FitsList[i], 'EXP_TIME', value='1.001',output_verify='ignore')
				hdr['EXP_TIME']= 15.001
				hdr.comments['EXP_TIME'] = 'A Mosiac of 2 x 15 second exposures'
				hdul.writeto(FitsList[i],output_verify='ignore',overwrite='True')
				exp_time = '15.001'
			readout_mode = hdr['READOUT']
			if imagetype == 'OBJECT':
				target = hdr['MSBTITLE']
			else:
				target = imagetype
			filter_ = hdr['FILTER']
			if exp_time in ['1.001','15.001']:
				file.write('{:<30} {:<10}{:<20}{:<10}*{:<10}{:<10}{:<10} '.format(FitsList[i],imagetype,target,filter_,exp_time,nexp,readout_mode))
			else:
				file.write('{:<30} {:<10}{:<20}{:<10}{:<10}{:<10}{:<10} '.format(FitsList[i],imagetype,target,filter_,exp_time,nexp,readout_mode))	
			file.write('\n')
			hdul.close()


	file.close()


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
  
