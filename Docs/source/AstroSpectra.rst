.. module:: AstroObject.AstroSpectra

Raw Spectrum Management :mod:`AstroSpectra`
*******************************************

An object and frame class which can handle raw spectrum data. This module only handles raw spectra. These spectra are simply data held in image-like frames. This class allows a spectrum to be consistently read and written to a FITS file, using image rows as data arrays. The spectra functions contained in this module are bland. For more sophisitcated spectral analysis, see the :mod:`AnalyticSpectra` module, which contians classes which can re-sample a raw spectrum and interpolate correctly across a spectrum to provide an analytic interface to otherwise discrete spectra.

.. warning:: The class implemented here does not yet use a sophisticated enough method for saving FITS header data etc. As such, it will not preserve state names etc. The development of this class should bring it inline with the STSCI spectra classes in the future.

.. autoclass::
    AstroObject.AstroSpectra.SpectraObject
    :members:
    :inherited-members:

.. autoclass::
    AstroObject.AstroSpectra.SpectraFrame
    :members:
    :special-members:


