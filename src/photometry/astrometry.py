# astrometry.py
#
# Script to dig through images directory and perform astrometry on the sidereal images
#
# Call from command python3 astrometry.py <directory> 
# -r to overwrite all files, otherwise exisitng files will be skipped


import numpy as np
import argparse
import os
import datetime
from astropy.io import fits
from photutils import Background2D, MedianBackground
from photutils import detect_threshold, detect_sources, source_properties
from astropy.stats import gaussian_fwhm_to_sigma
from astropy.convolution import Gaussian2DKernel
from astropy.wcs import WCS
from astroquery.astrometry_net import AstrometryNet


AstrometryNetKey = 'zfdyfzkcovyvwzie'

cardsToRemove = ['PV2_1', 'PV2_2', 'PV2_3']

#######################################################################################################################

# Open a FITS file and extract data
# Args: filename = string
# Return: metadata dictionary, image data array
def openFITS(filename):
	hdul = fits.open(filename)
	header = hdul[0].header
	data = hdul[0].data
	hdul.close()
	return header, data


# Save FITS file with provided data
# Args: filename = string, header = astropy header data dictionary, data = astropy image data
# Return: nothing
def saveFITS(filename, headerCards, data):
	hdu = fits.PrimaryHDU()
	hdu.data = data

	for key,value in headerCards.items():
		hdu.header[key] = value
	
	hdu.writeto(filename, overwrite=True)


# Make a clean new log file
# Args: nothing
# Returns: nothing
def createLog():
	f = open("errorLog.txt", "w")
	f.write("")
	f.close()


# Write a list of files which weren't succesful
# Args: badFile = string, error = string
# Returns: nothing
def appendLog(badFile, error):
	f = open("errorLog.txt", "a")
	f.write(badFile + " - " + error + "\n")
	f.close()


# Measure the background and make an interpolated background flux map
# Args: image = array of num
# Returns: bkg =
def measureBackground(image):
	bkg_estimator = MedianBackground()
	bkg = Background2D(image, (50, 50), filter_size=(3, 3), bkg_estimator=bkg_estimator)
	return bkg


# Subtract one image array from another, must be same size
# Args: image = array of num, subract = array of num
# Returns: subIm = array of num
def subtractImage(image, subtract):
	subIm = image - subtract
	return subIm


# Use image segmentation to find sources
# Args: image = array of num, FWHM = 3
# Returns: sources = 
def sourceDetection(image, FWHM = 3):
	threshold = detect_threshold(image, nsigma=1.0, background=0.0)

	sigma = FWHM * gaussian_fwhm_to_sigma
	kernel = Gaussian2DKernel(sigma, x_size=2, y_size=2)
	kernel.normalize()

	sources = detect_sources(image, threshold, npixels=5, filter_kernel=kernel)

	return sources


# Generate WCS info from a list of sources
# Args: sources = table of sources with pixel locations, imageWidth = num, imageHeight = num, pixelScale = num
# Returns: wcs = wcs header
def imageRegistration(sources, imageWidth, imageHeight, pixelScale):
	ast = AstrometryNet()
	ast.api_key = AstrometryNetKey

	sources.sort(['source_sum'], reverse=True)

	try_again = True
	submission_id = None

	while try_again:
		try:
			if not submission_id:
				wcs_header = ast.solve_from_source_list(sources['xcentroid'].value, sources['ycentroid'].value, imageWidth, imageHeight, scale_units='arcsecperpix', scale_type='ev', scale_est=pixelScale, scale_err=20, submission_id=submission_id, solve_timeout=300, publicly_visible='n', allow_commercial_use='n')
			else:
				wcs_header = ast.monitor_submission(submission_id, solve_timeout=300)
		
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
# Args: image = image data
# Returns: WCS header cards
def astrometry(image, pixelScale):

	#Background measurement
	background = measureBackground(image)

	#Background subtratcion
	image = subtractImage(image, background.background)

	#Source detection
	sources = sourceDetection(image)

	cat = source_properties(image, sources)
	columns = ['id', 'xcentroid', 'ycentroid', 'area', 'source_sum', 'source_sum_err']
	sourceStats = cat.to_table(columns=columns)

	#Only use 50 brightest sources for astrometry, and send off the nova.astrometry.net to plate solve
	sourceStats.sort(['source_sum'], reverse=True)
	wcs = imageRegistration(sourceStats[0:50], image.shape[0], image.shape[1], pixelScale)

	assert wcs is not False, "Failed astrometry!"
	
	return wcs #.to_header()


# Recursive function to go through directories and do astrometry on all applicable images
# Args: directory = path object
# Returns nothing
def astrometryAll(directory, overwrite=False):
	print("\n################################################################################\n")
	print("Checking everything in " + os.fsdecode(directory))

	# Iterate through files
	for file in os.listdir(directory):
		filename = os.fsdecode(file)

		# Check if sub-directory and enter if so
		if os.path.isdir(os.path.join(directory, file)):
			print("################################################################################")
			print("\n\"" + filename + "\" is a sub-directory, entering recursion level...\n")
			astrometryAll(os.path.join(directory, file), overwrite)

		else:
			# Check if in applicable sub-directory
			if not "Sidereal" in os.fsdecode(directory):
				print("\nNot a sidereal image directory, skipping!\n")
				continue

			# Check if applicable candidate file
			if filename.endswith("_r.fits"):
				candidate = filename
				cwd = os.getcwd()

				print("_______________________________________________________________________________")
				print("Found candidate file \"" + cwd+" "+candidate + "\", checking contents...")

				#Open file
				try:
					header, data = openFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))))
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to open!")
					print("Failed to open!")
					print(e)
					continue

				#Check if image has been reduced
				try:
					if not 'REDUCED' in header.keys():
						appendLog(os.fsdecode(candidate), "file not reduced!")
						print("\"" + candidate + "\" is not reduced, skipping!")
						continue
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to read atrribute!")
					print("Failed to read attribute!")
					print(e)
					continue

				# Extract image attributes
				try:
					obsTitle = header['MSBTITLE']
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to find attributes!")
					print("Failed to find attributes!")
					print(e)
					continue

				# Check if image is in fact sidereal
				if not "Sidereal" in obsTitle:
					# Something else = not relevant
					print("--- \"" + candidate + "\" is not a sidereal image, skipping!")
					continue

				# Check if solved file already exists
				if not overwrite and os.path.exists(os.path.join(directory, os.fsencode( candidate.split(".")[0] + "_a.fits" ))):
					print("\"" + candidate + "\" solved file already exists, skipping!")
					continue
				
				# Check header to see if astrometry Failed previously
				if 'Astrometry' in header and header['Astrometry'] == 'Failed':
					print("\"" + candidate + "\" Astrometric solution already attempted, skipping!")
					continue

				# Check header to see if astrometry Failed previously
				if 'WCSSLVD' in header and header['WCSSLVD'] == 'Failed':
					print("\"" + candidate + "\" Astrometric solution already attempted, skipping!")
					continue

				# Do the astrometry
				try:
					print("Solving for astrometry...")
					wcsData = astrometry(data, header['PIXLSIZE'])
				except Exception as e:
					header['WCSSLVD'] = 'Failed'
					saveFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))), header, data)
					appendLog(os.fsdecode(candidate), "failed to solve astrometry!")
					print("Failed to solve astrometry!")
					print(e)
					continue

				#Update header with new info
				header['WCSSLVD'] = 'Success'
				saveFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))), header, data)
				header.update(wcsData)
				
				
				
				# Add record to header for prosperity
				header["ASTROMET"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")

				# Remove cards which trigger PP unhappiness
				try:
					for c in cardsToRemove:
						header.remove(c)
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to remove bad cards!")
					print("Failed to remove bad cards!")
					print(e)
					continue

				# Save new FITS file with header cards and image data
				try:
					print("Saving file as \"" + candidate.split(".")[0] + "_a.fits\" ...")
					saveFITS(os.fsdecode(os.path.join(directory, os.fsencode( candidate.split(".")[0] + "_a.fits" ))), header, data)
					print("Success!")
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to save new file!")
					print("Failed to save new file!")
					print(e)
					continue



#######################################################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("directory", help="directory to start looking for files")
parser.add_argument("-r", "--overwrite", help="overwrite all files", action="store_true")

args = parser.parse_args()

createLog()
directory = os.fsencode(args.directory)
overwrite = args.overwrite


# cwd = os.getcwd()
# directory = os.path.join(os.fsencode(cwd), os.fsencode("temp"))
# overwrite = True



astrometryAll(directory, overwrite)

