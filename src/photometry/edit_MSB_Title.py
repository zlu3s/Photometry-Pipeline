# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 14:40:54 2026
@author: Zharnist
"""
from astropy.io import fits
import os

directory = "D:\\UKRIT_2021\\ToBeProcessed"

for root, dirs, files in os.walk(directory):
    for filename in files:
        if filename.endswith(".fit") or filename.endswith(".fits"):
            filepath = os.path.join(root, filename)
            hdul = fits.open(filepath, mode='update')
            try:
                title = hdul[0].header.get('MSBTITLE', '')
                obj = hdul[0].header.get('OBJECT', '')
                # Check either keyword for the original value
                if ('Sidereal' in title and title.strip() and not title.strip()[0].isdigit()) or \
                   ('Sidereal' in obj and obj.strip() and not obj.strip()[0].isdigit()):
                    print(f"Updating: {filepath}")
                    hdul[0].header['MSBTITLE'] = '99999_Sidereal_COSMOS'
                    hdul[0].header['OBJECT'] = '99999_Sidereal_COSMOS'
            finally:
                hdul.close(output_verify='ignore')