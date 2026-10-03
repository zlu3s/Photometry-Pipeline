
norad = ['12025','10677']
i=0
select_string_statement="""SELECT sats.norad_id, images.filter, images.start_time, targets.magnitude, targets.sun_elong_predicted
				FROM ((sats INNER JOIN targets ON sats.id = targets.target_id) INNER JOIN images ON targets.image_id = images.id)
				WHERE (sats.norad_id = """+norad[i]+"""
					  AND targets.rejected is NULL 
					  AND targets.magnitude IS NOT NULL
					  );"""
				
print(select_string_statement)
