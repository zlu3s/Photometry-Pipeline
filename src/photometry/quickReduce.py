# quickReduce.py
#
# Script to dig through images directory and perform a simple dark subtraction and flat fielding on the image data
#
# Call from command python3 quickReduce.py <directory> <darks> <flats>
# -r to overwrite all files, otherwise exisitng files will be skipped
# darks and flats can be a directory or singular file to override automatic matching

import numpy as np
from tqdm import tqdm
import argparse
import os
import datetime
from astropy.io import fits
from photutils import Background2D, MedianBackground




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



# Make a list of all files in a directory and all subdirectories
# Args: directory = path object
# Returns: list of path objects
def findAllFiles(directory):

	allFiles = []

	# Iterate through files
	for file in os.listdir(directory):

		# Check if sub-directory and enter if so
		if os.path.isdir(os.path.join(directory, file)):
			# Enter recursion level
			allFiles.extend( findAllFiles(os.path.join(directory, file)) )

		else:
			# Add to list
			allFiles.append(os.path.join(directory, file))

	return allFiles


# Search a directory and catalog the found dark or flat files
# Args: directory = path object
# Returns: dictionary of files organized by attributes, Exposure -> date:file
def catalogDarkFiles(directory):

	#tqdm.write("################################################################################")
	#tqdm.write("Searching for dark files and making catalog...")

	#Make empty dict
	catalog = {}

	# Find all files
	files = findAllFiles(directory)

	# Iterate through files
	for file in tqdm(files, desc="Making catalog of darks"):
		filename = os.fsdecode(file)
	
		# Check if applicable candidate file
		if filename.endswith(".fits"):
			candidate = filename

			#tqdm.write("_______________________________________________________________________________")
			#tqdm.write("Found candidate file \"" + candidate + "\", checking contents...")

			#Open file
			try:
				header, data = openFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))))
			except Exception as e:
				appendLog(os.fsdecode(candidate), "failed to open!")
				tqdm.write("Failed to open!")
				tqdm.write(e)
				continue

			# Extract image attributes
			try:
				obsType = header['OBSTYPE']
				date = datetime.datetime.strptime(header['DATE-OBS'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
				exposure = header['EXP_TIME']
			except Exception as e:
				appendLog(os.fsdecode(candidate), "failed to find attributes!")
				tqdm.write("Failed to find attributes!")
				tqdm.write(e)
				continue

			# Check if actually dark file
			if "DARK" not in obsType:
				#tqdm.write("---\"" + candidate + "\", is not a dark file, skipping!")
				continue

			# Sort into catalog
			#tqdm.write("Confirmed dark file, sorting into catalog...")
			try:
				if str(exposure) in catalog.keys(): 
					catalog[str(exposure)][ datetime.datetime.strftime(date,'%Y-%m-%d %H:%M:%S') ] = os.fsdecode(os.path.join(directory, os.fsencode(candidate)))
				else:
					catalog[str(exposure)] = { datetime.datetime.strftime(date,'%Y-%m-%d %H:%M:%S') : os.fsdecode(os.path.join(directory, os.fsencode(candidate))) }
			except Exception as e:
				appendLog(os.fsdecode(candidate), "failed to sort into catalog!")
				tqdm.write("Failed to sort into catalog!")
				tqdm.write(e)
				continue

			#tqdm.write("Done!")

	return catalog

# Search a directory and catalog the found dark or flat files
# Args: directory = path object
# Returns: dictionary of files organized by attributes, Filter -> Exposure -> date:file
def catalogFlatFiles(directory):

	#tqdm.write("################################################################################")
	#tqdm.write("Searching for flat files and making catalog...")

	#Make empty dict
	catalog = {}

	# Find all files
	files = findAllFiles(directory)

	# Iterate through files
	for file in tqdm(files, desc="Making catalog of flats"):
		filename = os.fsdecode(file)
	
		# Check if applicable candidate file
		if filename.endswith(".fits"):
			candidate = filename

			#tqdm.write("_______________________________________________________________________________")
			#tqdm.write("Found candidate file \"" + candidate + "\", checking contents...")

			#Open file
			try:
				header, data = openFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))))
			except Exception as e:
				appendLog(os.fsdecode(candidate), "failed to open!")
				tqdm.write("Failed to open!")
				tqdm.write(e)
				continue

			# Extract image attributes
			try:
				obsType = header['OBSTYPE']
				date = datetime.datetime.strptime(header['DATE-OBS'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
				color = header['FILTER'].strip()
				exposure = header['EXP_TIME']
			except Exception as e:
				appendLog(os.fsdecode(candidate), "failed to find attributes!")
				tqdm.write("Failed to find attributes!")
				tqdm.write(e)
				continue

			# Check if actually flat file
			if "FLAT" not in obsType and "SKYFLAT" not in obsType:
				#tqdm.write("---\"" + candidate + "\", is not a flat file, skipping!")
				continue

			# Sort into catalog
			#tqdm.write("Confirmed flat file, sorting into catalog...")
			try:
				if str(color) in catalog.keys(): 
					catalog[ str(color) ][ datetime.datetime.strftime(date,'%Y-%m-%d %H:%M:%S') ] = os.fsdecode(os.path.join(directory, os.fsencode(candidate)))
				else:
					catalog[ str(color) ] = { datetime.datetime.strftime(date,'%Y-%m-%d %H:%M:%S') : os.fsdecode(os.path.join(directory, os.fsencode(candidate))) } 

			except Exception as e:
				appendLog(os.fsdecode(candidate), "failed to sort into catalog!")
				tqdm.write("Failed to sort into catalog!")
				tqdm.write(e)
				continue

			#tqdm.write("Done!")

	return catalog


# Subtract one image array from another, must be same size
# Args: image = array of num, subract = array of num
# Returns: subIm = array of num
def subtractImage(image, subtract):
	subIm = image - subtract
	return subIm


# Divide an image array by the largest value within
# Args: image = array of num
# Returns: array of num
def normalizeImage(image):
	return image/np.max(image)


# Determine the 'gain' per pixel for flat fielding purposes
# Args: image = array of num
# Returns: array of num
def imageGain(image):
	return np.mean(image)/image


# Multiply one image array by another
# Args: image = array of num, multiply = array of num or num
# Return: array of num
def multiplyImage(image, multiply):
	return image * multiply


# Measure the background and make an interpolated background flux map
# Args: image = array of num
# Returns: bkg =
def measureBackground(image):
	bkg_estimator = MedianBackground()
	bkg = Background2D(image, (50, 50), filter_size=(3, 3), bkg_estimator=bkg_estimator)
	return bkg


# Do a simple image reduction with dark subtraction and flat field division
# Args: imageData = array of num, darkData = array of num, flatData = array of num or num
# Return: array of num
def quickReduce(imageData, darkData, flatData):

	#Check all data is same size and shape
	assert (imageData.shape == darkData.shape), "Image size does not match dark size!" 
	assert (imageData.shape == flatData.shape), "Image size does not match flat size!"
	
	#Subtract dark/bias from flat and science data
	flat = subtractImage(flatData, darkData)
	data = subtractImage(imageData, darkData)

	#Normalize the flat and divide from science data
	# flat = normalizeImage(flat)
	# data = multiplyImage(data, 1/flat)

	# Use flat fielding formula from wikipedia
	data = data * imageGain(flat)

	#Background measurement
	#background = measureBackground(data)

	#Background subtratcion
	#data = subtractImage(data, background.background)

	return data


# Recursive function to go through directories and reduce appicable image files
# Args: directory = path object, darks = dict or path object, flats = dict or path object
# Returns nothing
def quickReduceAll(directory, darks, flats, overwrite=False):
	#tqdm.write("\n################################################################################\n")
	#tqdm.write("Checking everything in " + os.fsdecode(directory))

	# Iterate through files
	for file in tqdm(os.listdir(directory), desc=os.fsdecode(directory)):
		filename = os.fsdecode(file)

		# Check if sub-directory and enter if so
		if os.path.isdir(os.path.join(directory, file)):
			#tqdm.write("################################################################################")
			#tqdm.write("\n\"" + filename + "\" is a sub-directory, entering recursion level...\n")
			quickReduceAll(os.path.join(directory, file), darks, flats, overwrite)

		else:
			# Check if applicable candidate file
			if filename.endswith(".fits"):
				candidate = filename

				#tqdm.write("_______________________________________________________________________________")
				#tqdm.write("Found candidate file \"" + candidate + "\", checking contents...")

				#Open file
				try:
					header, data = openFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))))
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to open!")
					tqdm.write("Failed to open!")
					tqdm.write(e)
					continue

				#Check if image has already been reduced before
				try:
					if 'REDUCED' in header.keys():
						#tqdm.write("\"" + candidate + "\" is alreday reduced, skipping!")
						continue
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to read atrribute!")
					tqdm.write("Failed to read attribute!")
					tqdm.write(e)
					continue

				# Extract image attributes
				try:
					obsType = header['OBSTYPE']
					date = datetime.datetime.strptime(header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
					color = header['FILTER'].strip()
					exposure = header['EXP_TIME']
					number_of_exposures = header['NEXP'] #added by Adam 2023-06-14
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to find attributes!")
					tqdm.write("Failed to find attributes!")
					tqdm.write(e)
					continue

				# Determine type of image
				if "OBJECT" in obsType:
					# Target or Sidereal image, do things below
					pass

				elif "DARK" in obsType:
					# Dark image
					#tqdm.write("--- \"" + candidate + "\" is a dark file, skipping!")
					continue

				elif "FLAT" in obsType:
					# Flat image
					#tqdm.write("--- \"" + candidate + "\" is a flat file, skipping!")
					continue

				else:
					# Something else = not relevant
					#tqdm.write("--- \"" + candidate + "\" is not a relevant file, skipping!")
					continue

				# Check if reduced file already exists
				if not overwrite and os.path.exists(os.path.join(directory, os.fsencode( candidate.split(".")[0] + "_r.fits" ))):
					#tqdm.write("\"" + candidate + "\" reduced file already exists, skipping!")
					continue

				# Find appropriate dark image and flat image
				#tqdm.write("\"" + candidate + "\" is a science image, now looking for darks and flats...")

				# Find a dark file
				try: 
					if type(darks) is dict:
						# Convert date strings back to datetime objects
						dates = map( lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'), darks[ str(exposure) ].keys() )
						# Find the closest date to the science image date
						closestDate = min( dates, key = lambda x: abs(date - x) )
						#Now find the corresponding file♫
						darkFile = darks[ str(exposure) ][ datetime.datetime.strftime(closestDate, '%Y-%m-%d %H:%M:%S') ]
					else:
						# Provided is not a file catalog, must be a single file override
						darkFile = os.fsdecode(darks)

				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to find dark!")
					tqdm.write("Failed to find dark!")
					tqdm.write(e)
					continue

				# Find a flat file
				try:
					if type(flats) is dict:
												
						# Convert date strings back to datetime objects
						dates = map( lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'), flats[ str(color) ].keys() )
						
						# Find the closest date to the science image date
						closestDate = min( dates, key = lambda x: abs(date - x) )
						#Now find the corresponding file
						flatFile = flats[ str(color) ][ datetime.datetime.strftime(closestDate, '%Y-%m-%d %H:%M:%S') ]
					else:
						# Provided is not a file catalog, must be a single file override
						flatFile = os.fsdecode(flats)

				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to find flat!")
					tqdm.write("Failed to find flat!")
					tqdm.write(e)
					continue				

				# Open dark file
				try:
					darkHeader, darkData = openFITS(os.fsdecode(os.path.join(directory, os.fsencode(darkFile))))
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to open dark file" + darkFile + "!")
					tqdm.write("Failed to open dark file!")
					tqdm.write(e)
					continue

				# Open flat file
				try:
					flatHeader, flatData = openFITS(os.fsdecode(os.path.join(directory, os.fsencode(flatFile))))
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to open flat file" + flatFile + "!")
					tqdm.write("Failed to open flat file!")
					tqdm.write(e)
					continue

				# Do the reduction
				try:
					#tqdm.write("Reducing image data...")
					#tqdm.write('Using {} for the dark frame.'.format(darkFile))
					#tqdm.write('Using {} for the flat field.'.format(flatFile))
					reData = quickReduce(data, darkData, flatData)
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to reduce!")
					tqdm.write("Failed to reduce!")
					tqdm.write(e)
					continue

				# Add record to header for prosperity
				header["REDUCED"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
				header["DARK"] = darkFile
				header["FLAT"] = flatFile

				# Save new FITS file with header cards and image data
				try:
					#tqdm.write("Saving file as \"" + candidate.split(".")[0] + "_r.fits\" ...")
					saveFITS(os.fsdecode(os.path.join(directory, os.fsencode( candidate.split(".")[0] + "_r.fits" ))), header, reData)
					#tqdm.write("Success!")
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to save new file!")
					tqdm.write("Failed to save new file!")
					tqdm.write(e)
				continue


#######################################################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("directory", help="directory to start looking for files")
parser.add_argument("darks", help="directory to find darks")
parser.add_argument("flats", help="directory to find flats")
parser.add_argument("-r", "--overwrite", help="overwrite all files", action="store_true")

args = parser.parse_args()

createLog()
directory = os.fsencode(args.directory)
overwrite = args.overwrite
darkFile = os.fsencode(args.darks)
flatFile = os.fsencode(args.flats)


# cwd = os.getcwd()
# directory = os.path.join(os.fsencode(cwd), os.fsencode("temp2"))
# overwrite = True
# darkFile = os.path.join(os.fsencode(cwd), os.fsencode("Darks/y20210115_00141.fits"))
# darkFile = os.path.join(os.fsencode(cwd), os.fsencode("Darks"))
# flatFile = os.path.join(os.fsencode(cwd), os.fsencode("Flats/Y/2021-01-30_FlatMaster-Y.fits"))
# flatFile = os.path.join(os.fsencode(cwd), os.fsencode("Flats"))


# Check if need to catalog darks and flats
if os.path.isdir(darkFile):
	darkFileCatalog = catalogDarkFiles( darkFile )
else:
	darkFileCatalog = darkFile

if os.path.isdir(flatFile):
	flatFileCatalog = catalogFlatFiles( flatFile )
else:
	flatFileCatalog = flatFile

# input("Press any key to continue...")

quickReduceAll(directory, darkFileCatalog, flatFileCatalog, overwrite)

