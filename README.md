---
 README
 Astronomy ObjectModel
 
 Created by Alexander Rudy on 2011-10-07.
 Copyright 2011 Alexander Rudy. All rights reserved.

  Version 0.2.0

---

# README

This program consists of a few simple objects for the repersentation and manipulation of astronomical objects. It allows python programs to interact with FITS files and Raw Data without constantly re-saving such data to the system. It provides a consistent object model, and stores object history for all of your data so that you won't lose data unintentionally.

There are two primary modules:

- AstroImage for handling images.
- AstroSpectra for handling 1D data like spectra.

AstroImage has some basic image manipulation features, and is designed to work quickly with IRAF. examples include dynamically writing a FITSFile and returning the filename to a pyRAF routine. For example:

imarith(ImageA.FITS(),+,ImageB.FITS(),"Out.FITS")

In the future, I will add the ability to import output fits files back in to the running object.

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
