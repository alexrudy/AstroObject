# AstroObject

AstroObject is a paradigm for manipulating Astronomical data in an object-oriented framework.

Documentation is hosted by GitHub Pages <http://alexrudy.github.com/AstroObject/>

## Frames and Objects

The primary structure of Object-Oriented astronomy data is the concept of **Frames** and **Stacks**. **Frames** are single pieces of data. **Stacks** are collections of **frames** which have a dictionary-like interface.

The concept is that you might have a single image, say ``Data.fits`` that you want to use for a lot of reduction. At the end of that work, you want to have the final result, and still have access to all of the intermediate states of that object. Normally, you might write numerous different FITS files to a diretory with names like ``flat_Data.fits`` or ``flatdarkbias_Data.fits``. This paradigm is a little silly. In ``AstroObject``, you would accomplish the same thing with:

```python
from AstroObject.AstroImage import ImageStack
Data = ImageStack(filename="Data.fits")
Data.read() # This will read "Data.fits", and save the data to frames with the name "Data".
Data["Biased"] = Data.d - BiasValue # Data.d gets the data from the latest state. Here, that is the raw data from "Data.fits"
Data["Flattened"] = Data.d / FlatValue # Data.d will get Data["Biased"] here, the most recent state.
Data["Scaled"] = numpy.sqrt(Data.d)
Data.write(clobber=True) # Makes a file Data.fits, which uses FITS extensions to store all of this inforamtion.
del Data["Scaled"] # Deletes the Scaled Data Frame
Data.show("Flattened") # Shows a matplotlib plot of the flattened data.
```	


## Simulators

The AstroObject module also has a simulator framework. The simulator is designed for easy command-line interface and dependency chaining of tasks. The simulator is writen with the concept of *stages*, which are semi-independent methods. *Stages* can have dependencies, and automatically implement error catching and logging features. As such, the simulator can be used for a multi-purpose command-line tool. See [the example simulator in the documentation]( http://alexrudy.github.com/AstroObject/SimulatorExample.html#simulatorexample).


# Release Notes

* 0.5-a1,a2
	- Alpha releases for testing the integration of IRAF tools

* 0.5.0
	- IRAF Tools and documentation thereof
* 0.4.0
	- Inheritance structure improved, now with abstract classes and mixins.
	- Documentation improved wildly, now everything except AstroCache is documented.
	- Header handling is greatly improved
	- Write-only attributes are now properties. Frame labels cannot be changed, instead, frame must be copied.
* 0.3.6
    - Matplotlib setuptools compatibility
* 0.3.5
    - Better version numbering
    - Use of the built-in NotImplementedError
* 0.3.4
    - Simulator can collect stages automatically
    - Simualtor can be setup using decorators on functions
    - Simulator can produces stage timing profiles
* 0.3.3
    - Stages provide description from function's docstring if no description is given.
    - Default keyword is used to set default stage operation.
* 0.3.2
    - Documentation, Documentation, Documentation
    - Added a `select` parameter to the save() function to allow the user to prevent automatic selection.
    - Pass `**kwargs` through a `data()` call to `__call__()`.
    - Uniform `KeyError` formatting support.
    - Simulator differentiates between stages which have been satisfied (`complete`) and stages which have actually run (`done`).
    - Simulator stage dependents will always run in simulator-registration order.
* 0.3.1
    - Dictionary methods for AstroObject (do things like AstroObject["Label"] = Frame)
    - Unified InterpolatedSpectrum model with various methods.
    - Simulator has better options controls (for configuration and arbitrary functions)
    - Cache module has been re-written. Now has a dict-like interface.
    - New configuration module
    - Unicode text in Simulator and AnalyticSpectra
* 0.3.0
	- New Simulator Module
	- New Caches Module
	- Unified Logging Module System
	- Setup.py Distribution
    - Unified Analytic Spectrum interface when using interpolation.
    - Unitary spectrum to collapse interpolated spectra early. 
    - Ability to resolve and resample analytic spectra.
* 0.2.9
	- Buildout compatiblity (Partially... buildout doesn't really work well with MatPlotLib, but its here in case that changes.)
	- Setup.py Fixes
		- dependencies have been lowered to coincide with UBUNTU package versions of things.
		- data file inclusion is now done through `data_files` which seems to work a little better
	- Now using distribute as a wrapper around setuptools to fix bugs etc.
	- **Note**: This is the LAST 0.2.x release. Future releases will be 0.2.9pX or 0.3.0 as new features are being introduced.
* 0.2.8
    - Release Notes for 0.2.7 and 0.2.8
* 0.2.7
	- Fix for missing VERSION file in `install`-ed package
* 0.2.6
	- Compatible with SetupTools setup.py paradigm
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
* 0.2.4
	- Better debugging information and errors from the AnaltyicSpectra.ResampledSpectra class's `resample()`
	- AstroSpectra's `__hdu__` includes header information stored in the HDU.
	- New utility function `npArrayInfo()` which handles array log messages for information about the array.
	- Testing updates to conform to new Resampling function (better example Spectra provided)
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
* 0.2.2
	- Hotfix to include updated notes in the README and to update documentation
* 0.2.1 
    - object.keep() only keeps the specified states
    - object.keep() and object.remove() both accept arbitrary numbers of arguments
    - derived classes now have a __valid__() method
    - object.object() has become object.frame() for more naming consistency. NOTE: object.object() will be depreciated.
    - AstroObject has been renamed AstroObjectBase to reflect its use as a base class. NOTE: AstroObject.AstroObject will be depreciated.
    - improvement to nosetests/spec
	- improvements to documentation
* 0.2.0
	- API Has CHANGED! Please see SPEC.md to understand the 0.2 API
* 0.1.4
	- Logging cannot capture warnings in python 0.1.4, so don't import that!
* 0.1.3
	- Handling Overflows in Blackbody Function
* 0.1.2
	- Logs only written to file when a "Logs/" folder is present.
* 0.1.1
	- Fixed a log message formatting error in AstroImage which caused a printing error
	- Removed the "Logs/" folder requirement from the module
* 0.1.0
	- Basic operation of Spectra
	- Basic operation of Images
	- Untested IRAF Interaction Lines
	- Basic FITS File Writing
	- NO Metadata and Header Features
	
