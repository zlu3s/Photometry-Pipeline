# findImage.py
#
# Search DB for matching file name and return attributes
#


# Find matching image
# Args: database cursor, file name
# Returns: list
def findImage(dbCursor, filename):

	#Search for matching file name in DB
	sql = "SELECT id, imageFile, start_time, exposure, filter FROM images WHERE imageFile = ?;"
	
	try:
		dbCursor.execute(sql, [filename])

		temp = [s for s in dbCursor]

		if len(temp) == 0:
			print("... no image found for", filename)
			return []
	except Exception as e:
		print("\tCould not find for", filename)
		print(e)
		return []

	return temp[0]




#TESTING

# import sqlite3

# databaseFile = "ukirt_2021-11-27.db"

# # Open database file (will create new one if not exist)
# try:
# 	print("Opening database...")
# 	conn = sqlite3.connect(databaseFile)
# except Exception as e:
# 	print("Failed!")
# 	print(e)
# 	exit()

# print("Success!")

# cursor = conn.cursor()

# #Test the thing
# temp = findImage(cursor, "y20210108_01126.fits")

# print(temp)

# #Commit changes to database
# conn.commit()
# conn.close()