#!/bin/bash
shopt -s extglob
cd /mnt/d/UKRIT_2021/ToBeProcessed;
for EachDateFolder in *; do
	if [ -d "$EachDateFolder" ]; then
    		cd $EachDateFolder; 
    		echo "Entering-->-->-->----->" $EachDateFolder; 
    		python3 /mnt/d/UKRIT_2021/Scripts/master_darks.py;
    		echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    		echo "Master Dark saved to /mnt/d/UKRIT_2021/Masters/Darks"
		echo "Also Created master dark in originating folder---------------->" $EachDateFolder;
		echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    		cd ..; 
    	fi;
done;
