# rebuildFITS.py
#
# Script to dig through directory and rebuild FITS files from separated header file and image data file
#
# Call from command python3 rebuildFITS <directory>
# -r to rebuild all files, otherwise exisitng rebuilt files will be skipped
#


import argparse
from tqdm import tqdm
import os
from astropy.io import fits
import warnings
from astropy.utils.exceptions import AstropyUserWarning

warnings.filterwarnings("ignore", category=AstropyUserWarning)

# Header cards to transfer
terms = ["DATE","ORIGIN","BSCALE","BZERO","HDUCLAS1","HDUCLAS2","HDSNAME","HDSTYPE","TELESCOP","INSTRUME","CAMNUM","DHSVER","HDTFILE","HDTFILE2","OBSERVER","USERID","OBSREF","PROJECT","SURVEY","SURVEY_I","MSBID","MSBTID","MSBTITLE","QUEUE","OPER_SFT","RQ_MINSB","RQ_MAXSB","RQ_MNSEE","RQ_MXSEE","RQ_MINCL","RQ_MAXCL","RQ_MNTAU","RQ_MXTAU","RQ_MINMN","RQ_MAXMN","RMTAGENT","AGENTID","OBJECT","RECIPE","OBSTYPE","OBSNUM","GRPNUM","GRPMEM","TILENUM","STANDARD","NJITTER","JITTER_I","JITTER_X","JITTER_Y","NUSTEP","USTEP_I","USTEP_X","USTEP_Y","NFOC","NFOCSCAN","UTDATE","DATE-OBS","DATE-END","GPS-OBS","GPS-END","MJD-OBS","WCSAXES","RADESYS","EQUINOX","TRACKSYS","CTYPE1","CTYPE2","CRPIX1","CRPIX2","CRVAL1","CRVAL2","CRUNIT1","CRUNIT2","CD1_1","CD1_2","CD2_1","CD2_2","PV2_1","PV2_2","PV2_3","RABASE","DECBASE","TELRA","TELDEC","GSRA","GSDEC","LST_OBS","LST_END","HABASE","TRAOFF","TDECOFF","AMSTART","AMEND","RARATE","DECRATE","APER_X","APER_Y","ISU2PORT","ISU2POFF","ISU2TOFF","GUIDING","GUIDFFOC","AGFREQ","FGMODE","IRPOLARM","DETECTOR","DETECTID","NINT","DROWS","DCOLUMNS","RDOUT_X1","RDOUT_X2","RDOUT_Y1","RDOUT_Y2","PIXLSIZE","PCSYSID","SDSUID","READMODE","CAPPLICN","CAMROLE","CAMPOWER","RUNID","READOUT","EXP_TIME","NEXP","READINT","NREADS","GAIN","BUNIT","AIRTEMP","BARPRESS","DEWPOINT","DOMETEMP","HUMIDITY","MIRR_NE","MIRR_NW","MIRR_SE","MIRR_SW","MIRRBTNW","MIRRTPNW","SECONDAR","TOPAIRNW","TRUSSENE","TRUSSWSW","TRUSSTOP","TRUSSBOT","WIND_DIR","WIND_SPD","CSOTAU","TAUDATE","TAUSRC","IZ5","HZ5SH","HZ5CH","HZ5SD","HZ5CD","IZ6","HZ6SH","HZ6CH","HZ6SD","HZ6CD","Z7","Z8","WEBEAM","NSBEAM","IZ9","HZ9SH","HZ9CH","HZ9SD","HZ9CD","IZ10","HZ10SH","HZ10CH","HZ10SD","HZ10CD","Z11","AAMP","APHI","TAMP","TPHI","CASSFOC","M2_X","M2_XD","M2_Y","M2_YD","M2_Z","M2_ZD","M2_U","M2_UD","M2_V","M2_VD","M2_W","TCS_FOC","TEL_FOFF","FOC_TOFF","FOC_POSN","FOC_ZERO","FOC_OFFS","FOC_FOFF","FILTER","DET_TEMP","DETTEMPB","DETTEMPS","DET_HTP","CCD_TEMP","CCDTEMPS","CCD_HTP","FS_TEMP","LNC_TEMP","SS_TEMP","M3_TEMP","TR_TEMP","RS_TEMP","CP_TEMP","SC_TEMP","CC_PRES","CNFINDEX"]


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


# Open a FITS file and extract data
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


# Rebuild the FITS file by combining the header and image data from two different files
# Args: headerFile = path like, imageFile = path like
# Return: nothing
def rebuildFITS(headerFile, dataFile):

	# Open files and separate headers from data
	try:
		dataHeader, data = openFITS(os.fsdecode(dataFile))
	except Exception as e:
		appendLog(os.fsdecode(dataFile), "failed to open")
		print("Failed!")
		print(e)
		return

	try:
		dataHeaderReal, dataFake = openFITS(os.fsdecode(headerFile))
	except Exception as e:
		appendLog(os.fsdecode(headerFile), "failed to open")
		print("Failed!")
		print(e)
		return

	# for key,value in dataHeaderReal.items():
	# 	print(key, " = ", value)
	# 	# print("\""+key+"\",")

	# Create new header
	hdu = fits.PrimaryHDU()

	# Transfer desired header cards
	for key in terms:
		try:
			hdu.header[key] = dataHeaderReal[key]
		except Exception as e:
			appendLog(os.fsdecode(headerFile), "failed to rebuild")
			print("Failed!")
			print(e)
			return

	#Save new FITS file with header cards and image data
	saveFITS(os.fsdecode(dataFile).split(".")[0] + ".fits", hdu.header, data)
	return


# Recursive function to go through directories and rebuild all the appicable files
# Args: directory = path object
# Returns nothing
def rebuildFiles(directory, rebuildAll=False):
	# Iterate through files
	for file in tqdm(os.listdir(directory), desc=os.fsdecode(directory)):
		filename = os.fsdecode(file)

		# Check if sub-directory and enter if so
		if os.path.isdir(os.path.join(directory, file)):
			rebuildFiles(os.path.join(directory, file), rebuildAll)

		else:
			# Check if header file
			if filename.endswith(".HEADER.fit"):
				headerFile = filename

				if not rebuildAll:
					# Check if rebuilt file already exists
					imageFile = headerFile.split(".")[0] + ".fits"
					if os.path.exists(os.path.join(directory, os.fsencode(imageFile))):
						continue

				# Now look for matching image data file
				dataFile = headerFile.split(".")[0] + ".I1.fit"
				if os.path.exists(os.path.join(directory, os.fsencode(dataFile))):
					# Rebuild FITS file
					rebuildFITS(os.path.join(directory, os.fsencode(headerFile)), os.path.join(directory, os.fsencode(dataFile)))

				else:
					appendLog(os.fsdecode(os.path.join(directory, os.fsencode(headerFile))), "no match")

			else:
				None


#######################################################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("directory", help="directory to start looking for files")
parser.add_argument("-r", "--rebuildAll", help="rebuild all files", action="store_true")

args = parser.parse_args()

createLog()
directory = os.fsencode(args.directory)
rebuildAll = args.rebuildAll

# cwd = os.getcwd()
# directory = os.fsencode(cwd)
# rebuildAll = True

rebuildFiles(directory, rebuildAll)

