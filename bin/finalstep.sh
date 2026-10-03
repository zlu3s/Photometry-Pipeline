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
					if [ "$FILTERFOLDER" == "Blank" ]; then  # Skip if folder name is "Blank"
						echo "Skipping a BLANK filter folder"
						continue #skips the entire iteration... 
					fi
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
cd /mnt/d/UKRIT_2021/NewlyProcessed;
for ProcessedDateFolder in *; do
	if [ -d "$ProcessedDateFolder" ]; then
    		cd $ProcessedDateFolder; 
    		echo "Entering-->-->-->----->" $ProcessedDateFolder;   
		for TARGETFOLDER in !(*Sidereal); do
			if [ -d "$TARGETFOLDER" ]; then
				cd $TARGETFOLDER;
				echo "--->---> Processing" $TARGETFOLDER;
				for FILTERFOLDER in *; do
					if [ "$FILTERFOLDER" == "Blank" ]; then  # Skip if folder name is "Blank"
						echo "Skipping a BLANK filter folder"
						continue #skips the entire iteration... 
					fi
					if [ -d "$FILTERFOLDER" ]; then
						cd $FILTERFOLDER;
						echo "--->--->---> Processing" $ProcessedDateFolder $TARGETFOLDER $FILTERFOLDER;
						pp_distill -positions positions.dat *r.fits;
						cd ..;
					fi;
				done;
				cd ..;	
			fi;
		done;
		cd ..;
		echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
		echo "Finalized things in---------------->" $ProcessedDateFolder;
		echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	fi;
done;
cd /mnt/d/UKRIT_2021/NewlyProcessed;

