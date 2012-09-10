Development Plans
=================

This section contains information and rough plans of items which are included for future development in the AstroObject Library

PyRAF Interaction
*****************
The module supports the writing and reading of IRAF temporary FITS files, to make code-side image manipulation much easier. Images can now be held in progam memory, and only written to slow disk IO when necessary. See the :mod:`IrafTools <AstroObject.iraftools` module.

Linear Fitting
**************
There will be a submodule built for fitting data, both a generic API and a linear fit object. These objects will include access to standard scientific fitting parameters, such as Chi-Squared and Normalized Residuals.

Binning
*******
I've been searching for a good, robust way to do image binning, but haven't found one. This is very useful for simulations as it allows us to over-sample simulated data. There is currently a :meth:`bin <AstroObject.util.images>` simple utility binning function which should work normally.

Analytic Convolutions
*********************
I'd like to develop a *fast* analytic way to do spectral convolutions. Managing individual spectra is okay, but handling a spectra that has a non-zero PSF, and hence is 2-D, is difficult. Generalizing this approach in the library is something I hope to do if I can figure this out.

Nearterm development
====================

Logging Framework
*****************

Shift logging framework logic as follows:
- Apply buffers to 'root' logger.
- Apply 'null' handlers to 'AstroObject' logger
- Configuration should apply to root logger. Logger class should facilitate access to root loggers.
- AstroSimulator should correctly configure low level logging
