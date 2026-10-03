# findReferenceStar.py
#
# Search DB for matching reference stars by date
#


# Find matching image
# Args: database cursor, filter character, datetime
# Returns: list
def findReferenceStar(dbCursor, filterChar, date):

	#Search for matching file name in DB
	sql = "SELECT referenceStars.zeropoint, referenceStars.zeropoint_error FROM referenceStars INNER JOIN images ON referenceStars.image_id = images.id WHERE strftime('%Y-%m-%d', images.start_time) = ? AND images.filter = ? AND referenceStars.rejected = 0;"
	
	try:
		# print([date.strftime('%Y-%m-%d'), filterChar])
		dbCursor.execute(sql, [date.strftime('%Y-%m-%d'), filterChar])

		temp = [s for s in dbCursor]

		if len(temp) == 0:
			print("... no reference stars found for", filterChar, date)
			return []
	except Exception as e:
		print("\tCould not find reference stars for", filterChar, date)
		print(e)
		return []

	print("...Found", len(temp), "reference stars...")

	return temp
