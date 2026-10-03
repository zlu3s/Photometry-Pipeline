# astrometryMT.py

#

# *** Mult-threaded version ***

#

# Script to dig through images directory and perform astrometry on the sidereal images

#

# Call from command python3 astrometryMT.py <directory> 

# -r to overwrite all files, otherwise exisitng files will be skipped

# -a to process all files even if not reduced, default will only process reduced files

# -p to provide the pixelscale in arcsec, should quicken the astrometry

# -b to subtract the background 

# change variable "redo_failed" to attempt to resolve failed images



import numpy as np

import argparse

import os

import datetime

import concurrent

import time



from astropy.io import fits

from photutils import Background2D, MedianBackground

from photutils import detect_threshold, detect_sources

from photutils import SourceCatalog

from astropy.stats import gaussian_fwhm_to_sigma

from astropy.convolution import Gaussian2DKernel

from astropy.wcs import WCS

from astroquery.astrometry_net import AstrometryNet

from astropy.coordinates import SkyCoord

from astropy import units as u



from log import *

from imageProcesses import *


redo_failed = False



AstrometryNetKey = 'zfdyfzkcovyvwzie'



cardsToRemove = ['PV2_1', 'PV2_2', 'PV2_3']





#######################################################################################################################



# Generate WCS info from a list of sources

# Args: sources = table of sources with pixel locations, imageWidth = num, imageHeight = num, pixelScale = num, radec = tuple of num

# Returns: wcs = wcs header

def imageRegistration(sources, imageWidth, imageHeight, pixelScale=None, radec=None):

	ast = AstrometryNet()

	ast.api_key = AstrometryNetKey



	sources.sort(['segment_flux'], reverse=True)



	try_again = True

	submission_id = None



	radec = None

	pixelScale = None



	while try_again:

		try:

			if not submission_id:

				if pixelScale is None and radec is None:

					wcs_header = ast.solve_from_source_list(sources['xcentroid'], sources['ycentroid'], imageWidth, imageHeight, submission_id=submission_id, solve_timeout=300, publicly_visible='n', allow_commercial_use='n')

				elif pixelScale is None:

					wcs_header = ast.solve_from_source_list(sources['xcentroid'], sources['ycentroid'], imageWidth, imageHeight, center_ra= radec[0], center_dec= radec[1], submission_id=submission_id, solve_timeout=300, publicly_visible='n', allow_commercial_use='n')

				elif radec is None:

					wcs_header = ast.solve_from_source_list(sources['xcentroid'], sources['ycentroid'], imageWidth, imageHeight, scale_units='arcsecperpix', scale_type='ev', scale_est=pixelScale, scale_err=20, submission_id=submission_id, solve_timeout=300, publicly_visible='n', allow_commercial_use='n')

				else:

					wcs_header = ast.solve_from_source_list(sources['xcentroid'], sources['ycentroid'], imageWidth, imageHeight, scale_units='arcsecperpix', scale_type='ev', center_ra= radec[0], center_dec= radec[1], scale_est=pixelScale, scale_err=20, submission_id=submission_id, solve_timeout=300, publicly_visible='n', allow_commercial_use='n')

			else:

				wcs_header = ast.monitor_submission(submission_id, solve_timeout=600)

		

		# except TimeoutError as e:

		except Exception as e:

			print(e)

			submission_id = e.args[1]

		else:

			# got a result, so terminate

			try_again = False



	if wcs_header:

		# Code to execute when solve succeeds

		return wcs_header

	else:

		# Code to execute when solve fails

		return False





# Solve image with astrometry.net

# Args: image = image data, pixelScale = num

# Returns: WCS header cards

def astrometry(image, pixelScale=None, radec=None, subBackground=True):



	if subBackground:

		#Background measurement

		background = measureBackground(image)



		#Background subtratcion

		image = subtractImage(image, background.background)



	#Source detection

	sources = sourceDetection(image)



	cat = SourceCatalog(image.astype('float32'), sources)

	columns = ['label', 'xcentroid', 'ycentroid', 'area', 'segment_flux', 'segment_fluxerr']

	sourceStats = cat.to_table(columns=columns)



	#Remove sources far from center which are more likely to be erroneous 

	remove = []



	for s in sourceStats:

		if s['xcentroid'] > (image.shape[0]-100) or s['xcentroid'] < (100) or s['ycentroid'] > (image.shape[1]-100) or s['ycentroid'] < (100):

			remove.append(s.index)



	sourceStats.remove_rows(remove)



	#Only use 50 brightest sources (skipping first 1 because it's probably a satellite streak) for astrometry, and send off the nova.astrometry.net to plate solve

	sourceStats.sort(['segment_flux'], reverse=True)

	wcs = imageRegistration(sourceStats[1:50], image.shape[0], image.shape[1], pixelScale, radec)



	assert wcs is not False, "Failed astrometry!"

	

	return wcs #.to_header()







# Function process each image

# Args: directory = path object, filename = string

# Returns nothing

def runAstrometryOperations(directory, filename, logFile="errorLog.txt", suffix="_r.fits", overwrite=False, reducedOnly=True, pixelScale = None, subBackground=True):

	

	print("Executing", filename, "on Process", os.getpid(), "..." )



	time.sleep(2)



	# Check if applicable candidate file

	if filename.endswith(suffix):

		candidate = filename



		print("_______________________________________________________________________________")

		print("Found candidate file \"" + candidate + "\", checking contents...")



		#Open file

		try:

			header, data = openFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))))

		except Exception as e:

			appendLog(logFile, os.fsdecode(candidate), "failed to open!")

			print("Failed to open!")

			print(e)

			return





		# data = data[0]

		



		#Check if image has been reduced

		if reducedOnly:

			try:

				if not 'REDUCED' in header.keys():

					appendLog(logFile, os.fsdecode(candidate), "file not reduced!")

					print("\"" + candidate + "\" is not reduced, skipping!")

					return

			except Exception as e:

				appendLog(os.fsdecode(candidate), "failed to read atrribute!")

				print("Failed to read attribute!")

				print(e)

				return



		# Check if solved file already exists

		if not overwrite and os.path.exists(os.path.join(directory, os.fsencode( candidate.split(".")[0] + "_a.fits" ))):

			print("\"" + candidate + "\" solved file already exists, skipping!")

			return


		# Check header to see if astrometry Failed previously
		if 'WCSSLVD' in header and header['WCSSLVD'] == 'Failed' and not redo_failed:
			print("\"" + candidate + "\" Astrometric solution already attempted, skipping!")
			return


		# Check for pointing info in header

		radec = None

		try:

			if 'RA' in header.keys() and 'DEC' in header.keys():

				c = SkyCoord(ra=header['RA'], dec=header['DEC'], unit=(u.hourangle, u.deg))

				radecGuess = (c.ra.hour, c.dec.deg)

				radec = radecGuess

				print("Image position is tagged as", radecGuess)

			else:

				print("No existing pointing info. Continuing with blind solve...")

		except Exception as e:

				appendLog(os.fsdecode(candidate), "failed to read atrribute!")

				print("Failed to read attribute!")

				print(e)

				return





		# Do the astrometry

		try:

			print("Solving for astrometry...{}".format(candidate))

			wcsData = astrometry(data, pixelScale, radec, subBackground)

		except Exception as e:

			appendLog(logFile, os.fsdecode(candidate), "failed to solve astrometry!")
			header['WCSSLVD'] = 'Failed'
			saveFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))), header, data)

			print("Failed to solve astrometry!")

			print(e)

			return



		#Update header with new info

		header.update(wcsData)
		header['WCSSLVD'] = 'Success'
		saveFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))), header, data)


		# Add record to header for prosperity

		header["ASTROMET"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")



		# Remove cards which trigger PP unhappiness

		try:

			for c in cardsToRemove:

				header.remove(c)

		except Exception as e:

			appendLog(logFile, os.fsdecode(candidate), "failed to remove bad cards!")

			print("Failed to remove bad cards!")

			print(e)

			return



		# Save new FITS file with header cards and image data

		try:

			print("Saving file as \"" + candidate.split(".")[0] + "_a.fits\" ...")

			saveFITS(os.fsdecode(os.path.join(directory, os.fsencode( candidate.split(".")[0] + "_a.fits" ))), header, data)

			print("Success!")

		except Exception as e:

			appendLog(logFile, os.fsdecode(candidate), "failed to save new file!")

			print("Failed to save new file!")

			print(e)

			return





# Recursive function to go through directories and do astrometry on all applicable images, runs multithreaded with a depth first approach

# Args: directory = path object

# Returns nothing

def astrometryAll(directory, logFile="errorLog.txt", suffix="_r.fits", overwrite=False, reducedOnly=True, pixelScale = None, subBackground=True):

	print("\n################################################################################\n")

	print("Checking everything in " + os.fsdecode(directory))



	waiting = []



	# Iterate through files

	for file in os.listdir(directory):

		filename = os.fsdecode(file)



		# Check if sub-directory and enter if so

		if os.path.isdir(os.path.join(directory, file)):

			print("################################################################################")

			print("\n\"" + filename + "\" is a sub-directory, entering recursion level...\n")

			astrometryAll(os.path.join(directory, file), logFile, suffix, overwrite, reducedOnly, pixelScale, subBackground)



		else:

			if filename.endswith(suffix):

				waiting.append(filename)



	# Make threads and run waiting files

	print("Starting multithreading...")

	

	executor = concurrent.futures.ProcessPoolExecutor(max_workers=8)

	futures = [executor.submit(runAstrometryOperations, directory, item, logFile, suffix, overwrite, reducedOnly, pixelScale, subBackground) for item in waiting]

	concurrent.futures.wait(futures)



	# runAstrometryOperations(directory, item, logFile, suffix, overwrite, reducedOnly, pixelScale, subBackground)

	

	# executor = concurrent.futures.ProcessPoolExecutor(max_workers=10)



	# for item in waiting:

	# 	executor.submit(runAstrometryOperations(directory, item, logFile, suffix, overwrite, reducedOnly, pixelScale, subBackground))





	print("Done multithreading.")



	

		







#######################################################################################################################



#Neede to guard against extra multi-processing becuz reasons

if __name__ == '__main__':   



	parser = argparse.ArgumentParser()

	parser.add_argument("directory", help="directory to start looking for files")

	parser.add_argument("-r", "--overwrite", help="overwrite all files", action="store_true")

	parser.add_argument("-a", "--allfiles", help="process all files even if not reduced", action="store_true")

	parser.add_argument("-p", "--pixelscale", help="pixel scale in arcsec")

	parser.add_argument("-b", "--subBackground", help="subtract the background", action="store_true")



	args = parser.parse_args()



	# Get current date+time for naming error log

	now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

	logFile =  now + "_astrometryLog.txt"



	createLog(logFile)



	suffix = "r.fits"





	directory = os.fsencode(args.directory)

	overwrite = args.overwrite

	reducedOnly = not args.allfiles

	if args.pixelscale is None:

		pixelScale = None

	else:

		pixelScale = float(args.pixelscale)

	subBackground = args.subBackground





	# cwd = os.getcwd()

	# directory = os.path.join(os.fsencode(cwd), os.fsencode("2020-10-20"))

	# overwrite = True

	# reducedOnly = True

	# pixelScale = 4.9

	# subBackground = False







	astrometryAll(directory, logFile, suffix, overwrite, reducedOnly, pixelScale, subBackground)



