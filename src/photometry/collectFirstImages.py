# collectFirstImages.py
#
# Script to dig through raw images directory, copy files and place them in constructed new directory
# Modified to only collect first image of each filter
#
# Call from command python3 collectFirstImages <directory> <destination>
# -r to overwrite all files, otherwise exisitng files will be skipped
#


import argparse
import os
import shutil
import re
import datetime
from astropy.io import fits




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


# Recursive function to go through directories and copy all the appicable files to a new directory
# Args: directory = path object, desintation = path object
# Returns nothing
def copyFiles(directory, destination, overwrite=False):
	print("Checking everything in " + os.fsdecode(directory))

	# Iterate through files
	for file in os.listdir(directory):
		filename = os.fsdecode(file)

		# Check if sub-directory and enter if so
		if os.path.isdir(os.path.join(directory, file)):
			print("################################################################################")
			print("\n\"" + filename + "\" is a sub-directory, entering recursion level...\n")
			copyFiles(os.path.join(directory, file), destination, overwrite)

		else:
			# Check if applicable candidate file
			if filename.endswith(".fits") and not filename.endswith("r.fits") and not filename.endswith("a.fits"):
				candidate = filename

				print("_______________________________________________________________________________")
				print("Found candidate file \"" + candidate + "\", checking contents...")

				#Open file
				try:
					header, data = openFITS(os.fsdecode(os.path.join(directory, os.fsencode(candidate))))
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to open!")
					print("Failed to open!")
					print(e)
					continue

				# Extract image attributes for sorting
				try:
					obsTitle = header['MSBTITLE']
					obsType = header['OBSTYPE']
					date = datetime.datetime.strptime(header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
					target = re.search("^\d+", obsTitle).group() if re.search("^\d+", obsTitle) else None
					color = header['FILTER'].strip()
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to find attributes!")
					print("Failed to find attributes!")
					print(e)
					continue

				# Determine type of image
				if "Sidereal" in obsTitle:
					# Sidereal image, Determine new directory
					#newDir = os.path.join(destination, os.fsencode(date.strftime("%Y-%m-%d")), os.fsencode(target + "_Sidereal"), os.fsencode(color))
					continue

				elif re.search("^\d+", obsTitle):
					# Target image, Determine new directory
					#newDir = os.path.join(destination, os.fsencode(date.strftime("%Y-%m-%d")), os.fsencode(target), os.fsencode(color))
					newDir = os.path.join(destination, os.fsencode(color))

				elif "DARK" in obsType:
					# Dark image
					print("--- \"" + candidate + "\" is a dark file, skipping!")
					continue

				elif "FLAT" in obsType:
					# Flat image
					print("--- \"" + candidate + "\" is a flat file, skipping!")
					continue

				else:
					# Something else = not relevant
					print("--- \"" + candidate + "\" is not a relevant file, skipping!")
					continue

				print("Determined desintation for \"" + candidate + "\" as \"" + os.fsdecode(newDir) + "\", now trying to copy...")

				# Check is copied file already exists
				if not overwrite and os.path.exists(os.path.join(newDir, os.fsencode(candidate))):
					print("\"" + candidate + "\" copied file already exists, skipping!")
					continue

				# Create the directory if not exist
				if not os.path.exists(newDir):
					try:
						os.makedirs(newDir)
						print("Made new directory \"" + os.fsdecode(newDir) + "\"...")
					except Exception as e:
						appendLog(os.fsdecode(candidate), "failed to make directory!")
						print("Failed to make directory!")
						print(e)
						continue

    			# Copy file to directory
				try: 
					shutil.copyfile(os.path.join(directory, os.fsencode(candidate)), os.path.join(newDir, os.fsencode(candidate)))
					print("Copied succesfully!")
				except Exception as e:
					appendLog(os.fsdecode(candidate), "failed to copy!")
					print("Failed to copy!")
					print(e)
					continue

				# Only copy first image then exit loop
				return


#######################################################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("directory", help="directory to start looking for files")
parser.add_argument("destination", help="destination to copy file to")
parser.add_argument("-r", "--overwrite", help="overwrite all files", action="store_true")

args = parser.parse_args()

createLog()
directory = os.fsencode(args.directory)
destination = os.fsencode(args.destination)
overwrite = args.overwrite

# cwd = os.getcwd()
# directory = os.path.join(os.fsencode(cwd), os.fsencode("20210115"))
# destination = os.path.join(os.fsencode(cwd), os.fsencode("new"))
# overwrite = False

copyFiles(directory, destination, overwrite)

