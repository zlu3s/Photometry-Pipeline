#!/bin/bash
shopt -s extglob
for TARGETFOLDER in !(*Sidereal); do
	if [ -d "$TARGETFOLDER" ]; then
		cd $TARGETFOLDER;
		echo "--->---> Processing" $TARGETFOLDER;
		echo
		#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
		#echo
		#echo "This is the first step for target data."
		#echo
		#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
		for FILTERFOLDER in *; do
			if [ -d "$FILTERFOLDER" ]; then
				if [ "$FILTERFOLDER" == "Blank" ]; then  # Skip if folder name is "Blank"
					echo "Skipping Blank folder"
					continue #skips the entire iteration... 
				fi
				cd $FILTERFOLDER;
				echo "--->--->---> Processing" $TARGETFOLDER $FILTERFOLDER;
				#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				#echo
				#echo "PP Prepare."
				#echo
				#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				pp_prepare -keep_wcs *r.fits;
				#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				#echo
				#echo "PP Photometry."
				#echo
				#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				pp_photometry -snr 3 -minarea 12 -aprad 6 *r.fits;
				#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				#echo
				#echo "PP Calibrate."
				#echo
				#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				pp_calibrate -instrumental *r.fits;
				echo
				cd ..;
			fi;
		done;
		cd ..;
		echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	fi;
done;
