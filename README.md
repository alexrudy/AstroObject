---
 README
 Astronomy ObjectModel
 
 Created by Alexander Rudy on 2011-10-07.
 Copyright 2011 Alexander Rudy. All rights reserved.

<<<<<<< HEAD
  Version 0.3.0a1
=======
  Version 0.3.0a2
>>>>>>> release/0.3.0a2

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
* 0.2.5
	- All `__init__` functions now accept arbitrary keywords, and all arguments to these functions are keywords. This shouldn't have any effect on currently implemented items, but new unittests will not test against non-keyword schemed inits
	- As such, the keyword for initializing data is always `data` and never `array`.
	- Changes to the `ResampledSpectrum` resample algorithm
		- Tightened tolerance on spectrum interpolation in resampled spectra.
		- Added a warning if you are resampling a spectrum to a higher resolution than the original source. The warning will not affect operation, but will message stdout
		- Now we clip zeros out of the flux, so that the resampled spectra will never return zero. The resulting value just won't be in the array.
	- Added the HDU-based frame and object system. The HDU system allows more direct manipulaton of HDUs. I'm still not confident in HDU's ability to preserve data during reads and writes. (Specifically writes, but I'm unsure about reads as well...)
	- `_default_state(self,states=None)` allows the user to filter states that you will use for the default collection
	- Prevented object `write()` function from taking the primary state from outside of the set of written states.
	- `write()` now uses the HDU header "LABEL" in order to set the state label
	- Removed initilaizng frame data from object initialization.
	- Added the `__version__` variable to all module components
	- `__all__` filtering for Utilities (and other modules)
	- `getVersion()` function which (by default) reads the `VERSION` file for version information.
	- `npArrayInfo()` handles data that isn't `np.ndarray` or isn't normal
	- Documentation of AstroFITS
	- Documentation of Utilities
* 0.2.6
	- Compatible with SetupTools setup.py paradigm
* 0.2.7
	- Fix for missing VERSION file in `install`-ed package
* 0.2.8
    - Release Notes for 0.2.7 and 0.2.8
* 0.2.9
	- Buildout compatiblity (Partially... buildout doesn't really work well with MatPlotLib, but its here in case that changes.)
	- Setup.py Fixes
		- dependencies have been lowered to coincide with UBUNTU package versions of things.
		- data file inclusion is now done through `data_files` which seems to work a little better
	- Now using distribute as a wrapper around setuptools to fix bugs etc.
	- **Note**: This is the LAST 0.2.x release. Future releases will be 0.2.9pX or 0.3.0 as new features are being introduced.
* 0.3.0a1
	**Alpha Release Software**
	- New Simulator Module
	- New Caches Module
	- Unified Logging Module System
	- Setup.py Distribution
* 0.3.0a2
	- Documentation for Logging System
	- Simulator Stability Improvements. **However** there are huge improvements coming in a later 0.3.0 alpha release. Please hold off until then for use of the simulator API or check out the features/dependencies branch of the repository to see that work in action.
	- Documentation of Simulator
	- Documentation of AnalyticSpectrum Objects
