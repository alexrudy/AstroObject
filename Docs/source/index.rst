.. AstroObject documentation master file, created by
    sphinx-quickstart on Tue Oct 18 23:50:03 2011.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Welcome to AstroObject!
=======================

AstroObject is a library for Object-Oriented Astronomy. Currently under development at `github`_, it contains tools for object-oriented management of Spectrum Data, Image Data, and Analytic Spectrum Data. More features are planned for the future. To get a sense of the philosophy of this project, read the introduction section.

AstroObject makes object-oriented astronomical data reduction easier. The systems provided in this package help to treat FITS images and other forms of raw data as objects. Critical to that mission is the notion that data are not just single images, but rather a series of images held together as they travel through the data reduction pipeline. As well, this module provides a framework for building dependency-based, flexible pipelines.

The goal of this package is not to facilitate specific image or analysis operations. Very few actual operations are built-in. Rather, it provides a structure, and a background to make working with data and reduction pipelines much easier. Abstracted are notions of files, configurations, and common reduction processes, and provided are simple command line interfaces, basic object-style APIs, and sensible defaults.

.. Warning::
    This module is under development. The version number |version| is very low, indicating that much of this module may be unreliable. The behavior in specific instances is not guaranteed nor should it be trusted. For more information about the development of this module, see :ref:`development`.

.. _Main_TOC:

About AstroObject
=================

*These pages are meant to be read for an understanding of what this module is good for. In the future, the tutorial will be here, as well as simple installation instructions, etc*.

.. toctree::
    :maxdepth: 2
    :numbered:
    
    intro
    installation
    AstroFITS
    AstroImage
    AstroSpectra
    AnalyticSpectra
    AstroNDArray
    AstroHDU
    iraftools
    AstroObject
    file
    AstroSimulator
    AstroConfig
    AstroObjectLogging
    Utilities
    
    future
    rnotes

.. _Examples_TOC:

Examples
========

.. toctree::
    
    examples/simulator
    examples/iraftools
    examples/spectra
    examples/pipeline
    

Testing and Development Features
================================

.. toctree::
	AstroTest

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _github: http://github.com/alexrudy/AstroObject/
