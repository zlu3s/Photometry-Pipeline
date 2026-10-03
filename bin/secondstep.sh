#!/bin/bash
shopt -s extglob
positionsfile="positions.dat";
cd /mnt/d/UKRIT_2021/NewlyProcessed;
for DATEFOLDER in 202*; do
	if [ -d "$DATEFOLDER" ]; then
		cd $DATEFOLDER;
		for TARGETFOLDER in !(*Sidereal); do
			if [ -d "$TARGETFOLDER" ]; then
				cd $TARGETFOLDER;
				
				for FILTERFOLDER in *; do
					echo "--->---> Processing" $DATEFOLDER $TARGETFOLDER $FILTERFOLDER;
					if [ -d "$FILTERFOLDER" ]; then
						cd $FILTERFOLDER;
						if [ ! -e "/mnt/d/UKRIT_2021/NewlyProcessed/$DATEFOLDER/$TARGETFOLDER/$FILTERFOLDER/$positionsfile" ]; then
							pp_manident *r.fits;
						else echo "These satellite images have already been manually identified.";
						fi;
						cd ..;
					fi;
				done;
				cd ..;
			fi;
		done;
		cd ..;
	fi;
done;
