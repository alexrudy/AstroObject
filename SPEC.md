
 SPEC
 ObjectModel
 
 Created by Alexander Rudy on 2011-10-13.
 Copyright 2011 Alexander Rudy. All rights reserved.
 
  Version 0.2.1

This file defines an interface specification for the Astro Object model. There are two types of objects defined here: Frames, which capture a specific instance of data, and Objects, which capture sets of frames, or whole FITS files, and provide the appropriate interface.


# FRAME
`__init__(label,header=None,metadata=None)` BaseClass

This function must save the provided label to the object.
The implementation of metadata and header data has not yet been finished.
	
`__call__(self)` Abstract

This function returns the data representation of the object. This will vary:
For Images: A 2-D numpy array in the image dimensions.
For Spectra: A 2-D numpy array, with the form [x,flux]
For Tables: Tables are not yet implemented

`__str__(self)` BaseClass

This function should return a string representation of the object

`__hdu__(self,primary=False)` Abstract

This function should generate an HDU for this frame. If the frame is empty, or can produce images, it can have the ability to generate a PrimaryHDU, as specified by the optional argument

`__show__(self)` Abstract

This function should call the minimal matplotlib calls to display with basic functionality

`@classmethod`
`__save__(cls,data,label,header=None,metadata=None)` Abstract

This function should determine if the passed data can be instantiated in this type, and if so, should instantiate such an object. If the data cannot be instantiated, it should raise an AbstractError.
	
`@classmethod`
`__read__(cls,HDU,label)` Abstract

This function is used to attempt to read this type of data. Only two actions may result:
On Success: Return an object of type cls with the HDU's data stored
On Failure: Raise an exception of type AbstractError describing the reason for failure.
	
# Spectra
Spectra are a special case. They are not two-dimensional images, and their scale is not inherently determined, nor is it standardized. As such, spectra are generally not reported with pixels, but rather with an abscissa axis. Spectra in the AstroObject system are stored in the following three possible ways:

1. *As Table Objects*: This will save the flux and wavelength in a two column table
2. *As an Image Object* : This will save the spectrum as an image, with the first row having flux, and second row having the wavelength equivalent.
3. *As a condensed Image Object*: This will save many spectra in the same primary HDU, in successive rows. For this method, all spectra must be provided with the same wavelength scale.

Primarily, I will implement method 2. This will be the default. This is the method used by [sdss DR5](http://www.sdss.org/dr5/products/spectra/read_spSpec.html)


