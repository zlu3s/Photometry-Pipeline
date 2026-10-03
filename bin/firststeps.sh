#!/bin/bash
shopt -s extglob
for ProcessedDateFolder in *; do
	if [ -d "$ProcessedDateFolder" ]; then
    		cd $ProcessedDateFolder;     	
    		echo "Entering-->-->-->-----/NewlyProcessed/" $ProcessedDateFolder; 
    		#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
		#echo
		#echo "Starting the First Step on Sidereal data."
		#echo
		#echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"  
		#~/firststepsidereal.sh;
		echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
		echo
		echo "Starting the First Step for TARGET data."
		echo
		echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
		~/firststeptarget.sh;
		echo "Completed All First Steps in---------------->/NewlyProcessed/" $ProcessedDateFolder;
		cd ..;
	fi;
done;
