Development Plans
=================

This section contains information and rough plans of items which are included for future development in the AstroObject Library

PyRAF Interaction
*****************
The module will support writing out temporary FITS files for PyRAF commands, and then re-loading this data in the program. This will allow the user to not worry about temporary files, and to save the full history state of their images in Python objects without the mechanics of reading and writing FITS files.

Linear Fitting
**************
There will be a submodule built for fitting data, both a generic API and a linear fit object. These objects will include access to standard scientific fitting parameters, such as Chi-Squared and Normalized Residuals.

