# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 11:16:40 2022

@author: ablock
"""


#!python
#
#Usage:
# 


from astropy.io import fits
import sys
import os

filekey ='y'   #the starting string common to the data file names
endkey = '.fits'

def main():
    
    
    
    #Set directory variable to be the type (bytes) read by os system 
    directory = os.fsencode('D:\\UKRIT_2021\\ToBeProcessed\\20220213\\temp')
    #change working directory
    os.chdir(directory)
    #FileList stores the Entire contents of directory- FitsList will be the data files
    FileList,FitsList = [],[]

    #create FileList and a list of Fits files
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        FileList.append(filename)
        if filename.startswith(filekey) and filename.endswith(endkey):
            FitsList.append(filename)
    if not FitsList:
           sys.exit("No files found in this directory that match your command line file listing. The file list is empty.")
    

    for i in range(len(FitsList)):
        print("...working on " + FitsList[i] + "...")
        #hdul = fits.open(FitsList[i])
        #hdr = hdul[0].header
        #hdr["MSBTITLE"] = '50463'
        fits.setval(FitsList[i], 'MSBTITLE', value='50463',output_verify='fix')
        #fits.setval(FitsList[i],'IMAGETYP',value='DARK')
        #fits.setval(FitsList[i],'EXPOSURE',value='120.00')
        #fits.setval(FitsList[i],'EXPTIME',value='120.00')
        #hdul.writeto(FitsList[i]+'_',overwrite=True)
       # hdul.close()

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()