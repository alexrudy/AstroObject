Analytic Spectra and Interpolation :mod:`AnalyticSpectra`
*********************************************************

Objects for manipulating and managing spectra which are inherently analytic (i.e. you want interpolation, or your spectrum to be defined by a single function).

This module contains a few pre-defined analytic spectra which you can use as examples. See the :mod:`AnalyticSpectraObjects` module.

.. module:: AnalyticSpectra
This module provides basic analytic spectrum capabilites. There is a simple principle at work in this module: Do all calculations as late as possible. As such, most spectra will be defined as basic analytic spectra. However, the use of the :class:`CompositeSpectra` class allows spectra to be used in mathematics::
    
    A = AnalyticSpectrum()
    B = AnaltyicSpectrum()
    C = A + B * 20
    


.. Note::
    I believe that STSCI Python has some spectrum capabilities, and I am researching combining this module to provide adaptors for the STSCI implementation.


.. autoclass::
    AnalyticSpectra.AnalyticSpectrum
    :members:
    :special-members:

.. autoclass::
    AnalyticSpectra.CompositeSpectra
    :members:
    :inherited-members:

Expansion Objects
-----------------

These objects provide simple expansions to the AnalyticSpectrum abstract class.

.. autoclass::
    AnalyticSpectra.InterpolatedSpectrum
    :members:
    :inherited-members:

.. autoclass::
    AnalyticSpectra.ResampledSpectrum
    :members:
    :inherited-members:
    

Analytic Spectrum Objects
-------------------------

These objects actually have spectral functions included.

.. autoclass::
    AnalyticSpectra.BlackBodySpectrum
    :members:
    :inherited-members:

.. autoclass::
    AnalyticSpectra.GaussianSpectrum
    :members:
    :inherited-members:

.. autoclass::
    AnalyticSpectra.FlatSpectrum
    :members:
    :inherited-members:
    
