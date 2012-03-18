.. module:: AstroObject.AnalyticSpectra

Analytic Spectra and Interpolation :mod:`AnalyticSpectra`
*********************************************************


Objects for manipulating and managing spectra which are inherently analytic (i.e. you want interpolation, or your spectrum to be defined by a single function). The classes provided in this module are *FRAMES* not *OBJECTS*, i.e. they are individual representations of spectra etc.

It is possible to create an AnalyticSpectraObject to hold many spectra. However, such an object might be of limited utility, as it could not be used to write or read data saved in FITS files, as the FITS format is not conducive to storing analytic items.

.. Note::
    This is a solvable problem. I could use FITS header information to store the required values for an analytic spectrum, and then simply store empty images. However, I don't need this capability now, so maybe in a future version.

This module contains a few pre-defined analytic spectra which you can use as examples. See the :mod:`AnalyticSpectraObjects` module.

This module provides basic analytic spectrum capabilites. There is a simple principle at work in this module: Do all calculations as late as possible. As such, most spectra will be defined as basic analytic spectra. However, the use of the :class:`CompositeSpectra` class allows spectra to be used in mathematics::
    
    A = AnalyticSpectrum()
    B = AnaltyicSpectrum()
    C = A + B * 20
    


.. Note::
    I believe that STSCI Python has some spectrum capabilities, and I am researching combining this module to provide adaptors for the STSCI implementation.


.. autoclass::
    AstroObject.AnalyticSpectra.AnalyticSpectrum
    :members:
    :special-members:

.. autoclass::
    AstroObject.AnalyticSpectra.CompositeSpectra
    :members:
    :inherited-members:
    
    .. automethod:: __call__

Expansion Objects
-----------------

These objects expand the concept of an analytic spectrum to be any spectrum which can respond to calls with arbitrary wavelength boundaries. The spectra in the :class:`InterpolatedSpectrum` class rely on a number of potential methods to calculate the desired wavelength values. The public methods for this class are generally the accepted potential resolution methods.

.. autoclass::
    AstroObject.AnalyticSpectra.InterpolatedSpectrum
    :members:
    :inherited-members:
    
    .. automethod:: __call__
    
    .. automethod:: _presanity
    
    .. automethod:: _postsanity

.. autoclass::
    AstroObject.AnalyticSpectra.Resolver
        
    .. automethod:: __call__

    
.. autoclass::
    AstroObject.AnalyticSpectra.UnitarySpectrum
        
    .. automethod:: __call__
    

Analytic Spectrum Objects
-------------------------

These objects actually have spectral functions included.

.. autoclass::
    AstroObject.AnalyticSpectra.BlackBodySpectrum
    :members:
    :inherited-members:
    
    .. automethod:: __call__
    

.. autoclass::
    AstroObject.AnalyticSpectra.GaussianSpectrum
    :members:
    :inherited-members:
    
    .. automethod:: __call__
    

.. autoclass::
    AstroObject.AnalyticSpectra.FlatSpectrum
    :members:
    :inherited-members:
    
    .. automethod:: __call__
    
    
