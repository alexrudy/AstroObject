---
 README
 Astronomy ObjectModel
 
 Created by Alexander Rudy on 2011-10-07.
 Copyright 2011 Alexander Rudy. All rights reserved.

  Version 0.2.4

---

# README

This program consists of a few simple objects for the repersentation and manipulation of astronomical objects. It allows python programs to interact with FITS files and Raw Data without constantly re-saving such data to the system. It provides a consistent object model, and stores object history for all of your data so that you won't lose data unintentionally.

Documentation is hosted by GitHub Pages <http://alexrudy.github.com/AstroObject/>

There are two primary modules:

- `AstroImage` for handling images.
- `AstroSpectra` for handling 1D data like spectra.

As well, the library is useful for building object-based representations of new data formats. The library comes with template classes that make it easy to expand the object oriented paradigm to whatever you are doing, and to add in custom manipulation functions.

# Release Notes

* 0.1.0
	- Basic operation of Spectra
	- Basic operation of Images
	- Untested IRAF Interaction Lines
	- Basic FITS File Writing
	- NO Metadata and Header Features
* 0.1.1
	- Fixed a log message formatting error in AstroImage which caused a printing error
	- Removed the "Logs/" folder requirement from the module
* 0.1.2
	- Logs only written to file when a "Logs/" folder is present.
* 0.1.3
	- Handling Overflows in Blackbody Function
* 0.1.4
	- Logging cannot capture warnings in python 0.1.4, so don't import that!
* 0.2.0
	- API Has CHANGED! Please see SPEC.md to understand the 0.2 API
* 0.2.1 
    - object.keep() only keeps the specified states
    - object.keep() and object.remove() both accept arbitrary numbers of arguments
    - derived classes now have a __valid__() method
    - object.object() has become object.frame() for more naming consistency. NOTE: object.object() will be depreciated.
    - AstroObject has been renamed AstroObjectBase to reflect its use as a base class. NOTE: AstroObject.AstroObject will be depreciated.
    - improvement to nosetests/spec
	- improvements to documentation
* 0.2.2
	- Hotfix to include updated notes in the README and to update documentation
* 0.2.3
	- Uniform `__init__` call signature (data,label,header=,metadata=)
	This will change to (**kwargs) in the next release. The signature will primarily use (data=,label=), so that can be included now for future compatibility.
	- Uniform `__call__` call signature for AnalyticSpectra items. This allows nested calls with a variety of keywords (see ResampledSpectrum)
	- New InterpolatedSpectrum (using Spline by default) and ResampledSpectrum objects provide analytic interfaces to data-based spectra.
	- AstroImage and AstroObject save header values to in `__hdu__` call.
	- AstroObject now has a `clobber` mode which allows `.save()` to overwrite data
	- AstroObject now has a `.clear()` method to delete all data.
	- Fixed a bug which might crop up when saving only a single frame to a FITS file in AstroObject.
	- AstroObject more consistently uses the `._default_state()` call to set statename.
	- Made a temporary fix for data copying bugs
	- Documentation of API
	- Documentation of AnalyticSpectra
	- Documentation includes examples
	- Documentation intro improved
	- Improvements to SpectraFrame `__show__()` plot limits
	- Improvements to messaging from AstroObject
	- Code style cleanup
	- `__all__` settings for modules
	- Testing for AnalyticSpectra
	- Testing for AstroImage functional test cases
	- Tests now include an API for functional testing
* 0.2.4
	- Better debugging information and errors from the AnaltyicSpectra.ResampledSpectra class's `resample()`
	- AstroSpectra's `__hdu__` includes header information stored in the HDU.
	- New utility function `npArrayInfo()` which handles array log messages for information about the array.
	- Testing updates to conform to new Resampling function (better example Spectra provided)


