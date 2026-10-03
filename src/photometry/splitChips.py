# splitChips.py
#
# Script to dig through directory and split full WFCAM images into 4 new files one for each chip
#
# Call from command python3 splitChips <directory>
#


import argparse
import os
from astropy.io import fits



#######################################################################################################################

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


# Recursive function to go through directories and split all the applicable files
# Args: directory = path object
# Returns nothing
def splitChips(directory):
	print("Checking everything in " + os.fsdecode(directory))

	# Iterate through files
	for file in os.listdir(directory):
		filename = os.fsdecode(file)

		# Check if sub-directory and enter if so
		if os.path.isdir(os.path.join(directory, file)):
			print("################################################################################")
			print("\n\"" + filename + "\" is a sub-directory, entering recursion level...\n")
			splitChips(os.path.join(directory, file))

		else:
			# Check if header file
			if filename.endswith(".fit"):

				print("Found \"" + filename + "\", attempting to split...")

				hdul = fits.open(os.fsdecode(os.path.join(directory, os.fsencode(filename))))

				# print(hdul.info())

				try:

					for i in range(1,len(hdul)):
						data = hdul[i].data

						primaryHeader = hdul[0].header
						# print(len(primaryHeader))
						secondaryHeader = hdul[i].header
						# print(len(secondaryHeader))

						primaryHeader.extend(secondaryHeader)#, update_first=True)
						# print(len(primaryHeader))
						# print(type(primaryHeader))

						primaryHeader.remove("CC_PRES", ignore_missing=True)

						newHDU = fits.PrimaryHDU(data,primaryHeader)
						newHDUL = fits.HDUList([newHDU])
						newHDUL.writeto(os.fsdecode(os.path.join(directory, os.fsencode(filename.rsplit( ".", 1 )[ 0 ] + "_" + str(i) + '.fits'))))

						print("Succesful!")

				except Exception as e:
					appendLog(os.fsdecode(filename), "failed to split")
					print("Failed!")
					print(e)
					continue


#######################################################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("directory", help="directory to start looking for files")

args = parser.parse_args()

createLog()
directory = os.fsencode(args.directory)

# cwd = os.getcwd()
# directory = os.fsencode(os.path.join(cwd,"CASUFlats"))


splitChips(directory)

