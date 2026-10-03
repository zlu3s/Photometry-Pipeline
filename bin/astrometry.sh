#!/bin/bash
shopt -s extglob
cd /mnt/d/UKRIT_2021/NewlyProcessed;
for DATEFOLDER in 202*; do
	if [ -d "$DATEFOLDER" ]; then
		cd $DATEFOLDER;
		for SIDEREALFOLDER in *Sidereal; do
			if [ -d "$SIDEREALFOLDER" ]; then
				cd $SIDEREALFOLDER;
				echo "--->---> Processing" $SIDEREALFOLDER;
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				echo
				echo "Doing Astrometry!."
				echo
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				for FILTERFOLDER in *; do
					if [ -d "$FILTERFOLDER" ]; then
						cd $FILTERFOLDER;
						echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
						echo
						echo "--->--->---> Astrometry Processing" $SIDEREALFOLDER $FILTERFOLDER;
						echo
						echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
						currentpath="/mnt/d/UKRIT_2021/NewlyProcessed/$DATEFOLDER/$SIDEREALFOLDER/$FILTERFOLDER"
						echo $currentpath
						python3 /mnt/d/UKRIT_2021/Scripts/astrometry.py $currentpath;
						cd ..;
					fi;
				done;
				cd ..;
			fi;
		done;
		cd ..;
	fi;
done;
