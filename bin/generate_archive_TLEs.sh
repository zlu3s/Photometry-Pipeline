#!/bin/bash
shopt -s extglob
cd /mnt/d/UKRIT_2021/ToBeProcessed;
for DATEFOLDER in *; do
	if [ -d "$DATEFOLDER" ]; then
		cd $DATEFOLDER;
		echo "--->--->---> Finding Contemporaneous TLEs in" $DATEFOLDER;
		python3 /mnt/d/UKRIT_2021/Scripts/generate_archive_TLEs.py /mnt/d/UKRIT_2021/ToBeProcessed/$DATEFOLDER /mnt/d/UKRIT_2021/TLE_Archive/archived_TLE_catalog_$DATEFOLDER.txt;
		echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++";
		cd ..;
	fi;
done;

