# log.py

#

# Functions for creating and writing error log files 





import datetime
import os





# Make a clean new log file

# Args: nothing

# Returns: nothing

def createLog(logFile):

	f = open(directory+logFile, "w")

	f.write("")

	f.close()





# Write a list of files which weren't succesful

# Args: badFile = string, error = string

# Returns: nothing

def appendLog(logFile, badFile, error):

	now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

	f = open(directory+logFile, "a")

	f.write(now + " - " + badFile + " - " + error + "\n")

	f.close()
	


directory = '/mnt/d/UKRIT_2021/NewlyProcessed/'
os.chdir(directory)