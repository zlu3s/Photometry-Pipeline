#!/bin/bash
shopt -s extglob
cd /mnt/d/UKRIT_2021/ToBeProcessed;
for DATEFOLDER in *; do
	if [ -d "$DATEFOLDER" ]; then
		cd $DATEFOLDER;
		echo "--->--->---> Scanning Header Files in" $DATEFOLDER;
		python3 /mnt/d/UKRIT_2021/Scripts/Ukirt_scan_Headers.py /mnt/d/UKRIT_2021/ToBeProcessed/$DATEFOLDER /mnt/d/UKRIT_2021/ToBeProcessed/$DATEFOLDER"/"$DATEFOLDER;
		cd ..;
	fi;
done;

