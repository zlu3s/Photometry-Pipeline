#!/bin/bash
shopt -s extglob;
export DISPLAY=:0;
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "Reattaching FITs headers to data files within the /mnt/d/UKRIT_2021/ToBeProcessed directory."
echo
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
python3 /mnt/d/UKRIT_2021/Scripts/rebuildFITS.py /mnt/d/UKRIT_2021/ToBeProcessed; 
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

