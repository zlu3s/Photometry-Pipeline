#!/bin/bash
shopt -s extglob;
export DISPLAY=:0;
~/scan_headers.sh;
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Reattaching FITs headers to data files within the /mnt/d/UKRIT_2021/ToBeProcessed directory."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
python3 /mnt/d/UKRIT_2021/Scripts/rebuildFITS.py /mnt/d/UKRIT_2021/ToBeProcessed; 
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Making Master Dark calibration files."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
~/createmasterdarks.sh;
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Building Directories in NewlyProcessed."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
python3 /mnt/d/UKRIT_2021/Scripts/buildimageDirectory.py /mnt/d/UKRIT_2021/ToBeProcessed  /mnt/d/UKRIT_2021/NewlyProcessed; 
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Generate TLEs- file searched are now the completed FITs from the above"
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
~/generate_archive_TLEs.sh;
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Running QuickReduce on the data files."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
python3 /mnt/d/UKRIT_2021/Scripts/quickReduce.py /mnt/d/UKRIT_2021/NewlyProcessed /mnt/d/UKRIT_2021/Masters/Darks /mnt/d/UKRIT_2021/Masters/CASU_Flats; 
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Using Astrometry.net to do blind plate solutions on images."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Current directory is now /mnt/d/UKRIT_2021/NewlyProcessed."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
cd /mnt/d/UKRIT_2021/NewlyProcessed;
~/astrometryMT.sh 1 & ~/astrometryMT_reverse.sh 2 & wait;
cd /mnt/d/UKRIT_2021/NewlyProcessed;
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "MasterScript is now handing off to (launching) firststeps.sh ."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
~/firststeps.sh;
~/finalstep.sh;
~/update_database.sh;
