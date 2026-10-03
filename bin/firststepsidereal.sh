#!/bin/bash
shopt -s extglob
for SIDEREALFOLDER in *Sidereal; do
	if [ -d "$SIDEREALFOLDER" ]; then
		cd $SIDEREALFOLDER;
		echo "--->---> Processing" $SIDEREALFOLDER;
		echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
		echo
		echo "This is the first/only step analysis of Sidereal data."
		echo
		echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
		for FILTERFOLDER in *; do
			if [ -d "$FILTERFOLDER" ]; then
				cd $FILTERFOLDER;
				echo "--->--->---> Processing" $SIDEREALFOLDER $FILTERFOLDER;
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				echo
				echo "PP Prepare."
				echo
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				pp_prepare -keep_wcs *a.fits;
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				echo
				echo "PP Photometry."
				echo
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				pp_photometry *a.fits;
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				echo
				echo "PP Calibrate."
				echo
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				pp_calibrate *a.fits;
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				echo
				echo "PP Distill."
				echo
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				pp_distill *a.fits;
				cd ..;
			fi;
		done;
		cd ..;
	fi;
done;
