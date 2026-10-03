#!/bin/bash
shopt -s extglob
for TARGETFOLDER in *Sidereal; do
	if [ -d "$TARGETFOLDER" ]; then
		cd $TARGETFOLDER;
		echo "Entering " $TARGETFOLDER;
		for FILTERFOLDER in *; do
			if [ -d "$FILTERFOLDER" ]; then
				cd $FILTERFOLDER;
				echo "Entering and listing *a.fits files in " $TARGETFOLDER $FILTERFOLDER;
				echo "PlateSolvedFiles"
				ls *a.fits
				cd ..;
			fi;
		done;
		cd ..;
	fi;
done;
