#!/bin/bash
shopt -s extglob
cd /mnt/d/UKRIT_2021/TLE_Archive/;
for TLEFILE in *.txt; do
	python3 /mnt/d/UKRIT_2021/Scripts/Database/insertTLEFile.py /mnt/d/UKRIT_2021/TLE_Archive/$TLEFILE /mnt/d/UKRIT_2021/Database/ukirt.db; 
done;
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Process Database."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
python3 /mnt/d/UKRIT_2021/Scripts/Database/postProcessDB.py /mnt/d/UKRIT_2021/Database/ukirt.db; 
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "D O N E"
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
