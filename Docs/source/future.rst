Development Plans
=================

This section contains information and rough plans of items which are included for future development in the AstroObject Library

PyRAF Interaction
*****************
The module will support writing out temporary FITS files for PyRAF commands, and then re-loading this data in the program. This will allow the user to not worry about temporary files, and to save the full history state of their images in Python objects without the mechanics of reading and writing FITS files.

Linear Fitting
**************
There will be a submodule built for fitting data, both a generic API and a linear fit object. These objects will include access to standard scientific fitting parameters, such as Chi-Squared and Normalized Residuals.

Binning
*******
I've been searching for a good, robust way to do image binning, but haven't found one. This is very useful for simulations as it allows us to over-sample simulated data.

Analytic Convolutions
*********************
I'd like to develop a *fast* analytic way to do spectral convolutions. Managing individual spectra is okay, but handling a spectra that has a non-zero PSF, and hence is 2-D, is difficult. Generalizing this approach in the library is something I hope to do if I can figure this out.