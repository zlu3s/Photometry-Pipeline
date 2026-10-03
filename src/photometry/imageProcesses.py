# imageProcesses.py

# 

# Functions for dealing image files and image data

#



import numpy as np

from astropy.io import fits

from photutils.background import Background2D, MedianBackground
from photutils.segmentation import detect_threshold, detect_sources

from photutils.segmentation import deblend_sources

from astropy.stats import gaussian_fwhm_to_sigma

from astropy.convolution import Gaussian2DKernel,convolve




import copy





# Open a FITS file and extract data

# Args: filename = string

# Return: metadata dictionary, image data array

def openFITS(filename):

	hdul = fits.open(filename, mode='update')

	header = copy.deepcopy(hdul[0].header)

	data = copy.deepcopy(hdul[0].data)

	hdul.close(closed=True)

	return header, data





# Save FITS file with provided data

# Args: filename = string, header = astropy header data dictionary, data = astropy image data

# Return: nothing

def saveFITS(filename, headerCards, data, bit='int32'):

	hdu = fits.PrimaryHDU()

	hdu.data = data



	for key,value in headerCards.items():

		hdu.header[key] = value



	hdu.scale(bit)



	hdu.writeto(filename, overwrite=True)





# Subtract one image array from another, must be same size

# Args: image = array of num, subract = array of num

# Returns: subIm = array of num

def subtractImage(image, subtract):

	subIm = image - subtract

	return subIm





# Divide an image array by the largest value within

# Args: image = array of num

# Returns: array of num

def normalizeImage(image):

	return image/np.max(image)





# Determine the 'gain' per pixel for flat fielding purposes

# Args: image = array of num

# Returns: array of num

def imageGain(image):

	return np.mean(image)/image





# Multiply one image array by another

# Args: image = array of num, multiply = array of num or num

# Return: array of num

def multiplyImage(image, multiply):

	return image * multiply





# Measure the background and make an interpolated background flux map

# Args: image = array of num

# Returns: bkg =

def measureBackground(image):

	bkg_estimator = MedianBackground()

	bkg = Background2D(image, (50, 50), filter_size=(3, 3), bkg_estimator=bkg_estimator)

	return bkg





# Use image segmentation to find sources, background = None will compute a background map

# Args: image = array of num, FWHM = 3

# Returns: sources = 


def sourceDetection(image, FWHM=1.5, npixels=5, nsigma=1.0):
	threshold = detect_threshold(image, nsigma=nsigma, background=None)
	sigma = FWHM * gaussian_fwhm_to_sigma
	kernel = Gaussian2DKernel(sigma, x_size=2, y_size=2)
	kernel.normalize()
	# Convolve first, then detect
	convolved_image = convolve(image, kernel)
	sources = detect_sources(convolved_image, threshold, npixels=npixels)
	return sources







