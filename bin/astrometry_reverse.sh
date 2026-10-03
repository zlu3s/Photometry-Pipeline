#!/bin/bash
shopt -s extglob
cd /mnt/d/UKRIT_2021/NewlyProcessed;
dirlist=$(ls -d 202*);
revlist=$(echo $dirlist|tr ' ' '\n'|tac|tr '\n' ' ');
echo $revlist;
for DATEFOLDER in $revlist; do
	echo $DATEFOLDER
	if [ -d "$DATEFOLDER" ]; then
		cd $DATEFOLDER;
		sidereallist=$(ls -d *Sidereal);
		revsidereallist=$(echo $sidereallist|tr ' ' '\n'|tac|tr '\n' ' ');
		echo $revsidereallist;
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
				echo $revfilterlist;
				for FILTERFOLDER in $revfilterlist; do
					if [ -d "$FILTERFOLDER" ]; then
						cd $FILTERFOLDER;
						echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
						echo
						echo "--->--->---> Astrometry Processing" $SIDEREALFOLDER $FILTERFOLDER;
						echo
						echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
						currentpath="/mnt/d/UKRIT_2021/NewlyProcessed/$DATEFOLDER/$SIDEREALFOLDER/$FILTERFOLDER"
						echo $currentpath
						SECONDS = 0;
						python3 /mnt/d/UKRIT_2021/Scripts/astrometry.py $currentpath;
						duration=$SECONDS;
						echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed to complete the $FILTERFOLDER of $SIDEREALFOLDER in $DATEFOLDER";
						cd ..;
					fi;
				done;
				cd ..;
			fi;
		done;
		cd ..;
	fi;
done;
