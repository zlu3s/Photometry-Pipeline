#!/bin/bash
shopt -s extglob
cd /mnt/d/UKRIT_2021/NewlyProcessed/2021-08-09;

		sidereallist=$(ls -d *Sidereal);
		revsidereallist=$(echo $sidereallist|tr ' ' '\n'|tac|tr '\n' ' ');
		for SIDEREALFOLDER in $revsidereallist; do
			if [ -d "$SIDEREALFOLDER" ]; then
				cd $SIDEREALFOLDER;
				echo "--->---> Processing" $SIDEREALFOLDER;
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				echo
				echo "Doing Astrometry!."
				echo
				echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				filterlist=$(ls -d *);
				revfilterlist=$(echo $filterlist|tr ' ' '\n'|tac|tr '\n' ' ');
				for FILTERFOLDER in $revfilterlist; do
					if [ -d "$FILTERFOLDER" ]; then
						cd $FILTERFOLDER;
						echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
						echo
						echo "--->--->---> Astrometry Processing" $SIDEREALFOLDER $FILTERFOLDER;
						echo
						echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
						currentpath="/mnt/d/UKRIT_2021/NewlyProcessed/2021-08-09/$SIDEREALFOLDER/$FILTERFOLDER"
						echo $currentpath
						python3 /mnt/d/UKRIT_2021/Scripts/astrometry.py $currentpath;
						cd ..;
					fi;
				done;
				cd ..;
			fi;
		done;
		cd ..;
