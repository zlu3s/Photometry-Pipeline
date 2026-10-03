#!/bin/bash
shopt -s extglob
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Navigating to UKRIT->Database directory"
echo "Creating Empty SQL DataBase"
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
cd /mnt/d/UKRIT_2021/Database/;
python3 /mnt/d/UKRIT_2021/Scripts/Database/createDatabase.py; 
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
read -p "Press any key to resume ...";
echo
echo "Populate Database with Images, Sidereal references, Target measurements and Rejection lists"
echo "Source DRIVE A (archived)"
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
cd /mnt/a/UKRIT_2021/Database/;
python3 /mnt/d/UKRIT_2021/Scripts/Database/populateDB.py /mnt/a/UKRIT_2021/ProcessedImages /mnt/d/UKRIT_2021/Database/ukirt.db -i; 
python3 /mnt/d/UKRIT_2021/Scripts/Database/populateDB.py /mnt/a/UKRIT_2021/ProcessedImages /mnt/d/UKRIT_2021/Database/ukirt.db -s; 
python3 /mnt/d/UKRIT_2021/Scripts/Database/populateDB.py /mnt/a/UKRIT_2021/ProcessedImages /mnt/d/UKRIT_2021/Database/ukirt.db -t; 
python3 /mnt/d/UKRIT_2021/Scripts/Database/populateDB.py /mnt/a/UKRIT_2021/ProcessedImages /mnt/d/UKRIT_2021/Database/ukirt.db -r; 
echo
echo
echo
echo "Populate Database with Images, Sidereal references, Target measurements and Rejection lists"
echo "Source DRIVE D (current)"
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
python3 /mnt/d/UKRIT_2021/Scripts/Database/populateDB.py /mnt/d/UKRIT_2021/ProcessedImages /mnt/d/UKRIT_2021/Database/ukirt.db -i; 
python3 /mnt/d/UKRIT_2021/Scripts/Database/populateDB.py /mnt/d/UKRIT_2021/ProcessedImages /mnt/d/UKRIT_2021/Database/ukirt.db -s; 
python3 /mnt/d/UKRIT_2021/Scripts/Database/populateDB.py /mnt/d/UKRIT_2021/ProcessedImages /mnt/d/UKRIT_2021/Database/ukirt.db -t; 
python3 /mnt/d/UKRIT_2021/Scripts/Database/populateDB.py /mnt/d/UKRIT_2021/ProcessedImages /mnt/d/UKRIT_2021/Database/ukirt.db -r; 
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Insert TLE Files into Database"
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
cd /mnt/d/UKRIT_2021/TLE_Archive/;
rm error*.txt;
for TLEFILE in *.txt; do
	python3 /mnt/d/UKRIT_2021/Scripts/Database/insertTLEFile.py /mnt/d/UKRIT_2021/TLE_Archive/$TLEFILE /mnt/d/UKRIT_2021/Database/ukirt.db; 
done;
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Process Database."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
python3 /mnt/d/UKRIT_2021/Scripts/Database/postProcessDB.py /mnt/d/UKRIT_2021/Database/ukirt.db -e; 
python3 /mnt/d/UKRIT_2021/Scripts/Database/postProcessDB.py /mnt/d/UKRIT_2021/Database/ukirt.db -z; 
python3 /mnt/d/UKRIT_2021/Scripts/Database/postProcessDB.py /mnt/d/UKRIT_2021/Database/ukirt.db -m; 
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Add Satellite MetaData."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
python3 /mnt/d/UKRIT_2021/Scripts/Database/addSatsMetadata.py /mnt/d/UKRIT_2021/Database/ukirt.db; 
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "D O N E"
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
