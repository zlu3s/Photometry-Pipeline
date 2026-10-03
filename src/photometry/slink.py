# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 20:19:09 2022

@author: ablock
"""

from starlink import sdf
print('success')
hdul = sdf.open('u20220427_00036.sdf')
hdr = hdul[0].header
allofthem = hdr.keys()
for key in allofthem:
	print(key,hdr[key])