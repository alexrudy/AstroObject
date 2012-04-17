.. currentmodule:: AstroObject

Introduction to :mod:`AstroObject`
==================================

Welcome to AstroObject, a library for managing Astronomical Data. The idea behind this library is to bring Astronomical data and data reduction into the object-oriented age. This library is not meant for use with what astronomers lovingly call "codes", but rather is designed with full fledged programs in mind.

With that in mind, it is good to know that this module is based around two concepts, **Objects** and **Frames**. 

Often, when doing data reduction, you end up manipulating the same image or spectra many times. This process (in my experience) has led me to litter my directories with numerous FITS files, always prepending or appending ``b`` or some other character to indicate the current state of the image. This module allows you to think of each of those states of the same image as a **frame**, all belonging to the same image **object**.

It just so happens that the FITS data format supports this understanding as well, by way of FITS extensions. As such, you can store your beautifully reduced science image in the front of a FITS image, but include a full history of that image in subsequent FITS extension frames. Of course, this might make for rather large FITS files, so this library makes no assumptions about how you write FITS files at the end of the day.

.. Note:: The terms **Object** and **Frame** are used throughout the documentation here. Unfortunately, *object* has a different meaning in python. In this documentation, when I refer to a python-style *object*, I will use *italics*, and when I refer to an AstroObject style **object**, I will use **bold**. For clarity and emphasis sake, I will also try to use **bold** when refering to AstroObject-style **frames**

Frames
******

A **frame** is a single instance of data. It doesn't have to be image data, it could instead be spectral data, or any other data you could think of. The point is that a **frame** is just one instance of such data. Each **frame** in :mod:`AstroObject` has a label, and each **frame** can carry its own data as well as its own metadata.

The format of data in a **frame** depends on what type of **frame** you want to use. For the simple :mod:`AstroObject.AstroImage` implementation, a **frame** is a two-dimensional array of numpy data (along with a stack of other meta-data that it gets to carry around). You should really only write to a **frame** once (although sometimes you may need a place to put an image temporarily, and then wish to over-write it or delete it later... that is perfectly fine), and then that **frame** will preserve the image data for you.

The :mod:`AstroObject` module comes with a variety of **frames**, and it is easy to create your own. The required functions for each **frame** are documented in :ref:`AstroObjectAPI`, and a template class is provided in :class:`AstroObjectBase.BaseFrame`. However, if you want to work with images, you can use **frames** from :mod:`AstroObject.AstroImage`, and if you want to work with spectra, you can use **frames** from :mod:`AstroObject.AstroSpectra` and :mod:`AstroObject.AnalyticSpectra`.

Object
******

**Objects** are really just collections of **frames** with a few additional helpful features. When you reduce an image, you really only care about a single image, and most of the time, you want the most recent changes to that image. That is where **objects** help. Instead of storing innumerable FITS files, you just add each **frame** (image) to a single **object**. Then, you can use that **object**'s methods to easily retrieve and store new data.

**Objects** provide smart :meth:`save` methods which allow you to pass either an already instantiated :meth:`frame` or just the raw data you wish to store. Then, to retrieve your data, you can ask an object for the :meth:`frame` or the raw data. All of these methods are documented at :class:`AstroObjectBase.BaseObject`.

If you intend to use **objects** and **frames** built into :mod:`AstroObject`, then you really don't need to worry about the implementaion of **frames**, in fact, you should be able to do everything you need, just knowing that a **frame** is a python-style *object* you can pass around, and using the methods provided by **objects**

Simulators
**********

Simulators are complex task management tools which provide a command line interface, and dependency chain resolution. They help to structure and run large bodies of code, especially those that might have complex dependency chains, and may need multiple modes of operation. The basic principle is to design long programs as a single class isntance, with methods attached for each important function in the **simulator**. The module will then handle each of these instance methods as a **stage** which can be run independtly from each other. Normally, **stages** will depend on each other to run, and so a chain of dependencies can be built. As well, **simulator** tries to handle exceptions and loops gracefully, and provides methods to loop over various collections. See :mod:`AstroObject.AstroSimulator`.

Library Users
*************

General users should, when examining basic AstroObject functionality, understand the use of **objects**, and understand what **frames** are, but not necessarily their instance methods or uses. All normal operations can be handled by the **object** model in :mod:`AstroObject`. As well, general users might use the :mod:`AstroObject.AstroSimulator` tool, and may also wish to examine :mod:`AstroObject.AstroConfig` for information about configuration objects and ``yaml`` based configurations.

For modules which specifically handle ceratin functions, see:

- Images: See :mod:`AstroObject.AstroImage`
- Spectral Data: See :mod:`AstroObject.AstroSpectra`
- Analytic and manipulated Spectra: See :mod:`AstroObject.AnalyticSpectra`
- Empty FITS Files: See :mod:`AstroObject.AstroObjectBase`
- Advanced FITS HDUs: See :mod:`AstroObject.AstroFITS`
- Command-line Tools and Complex Tasks: See :mod:`AstroObject.AstroSimulator`
- Configuration: See :mod:`AstroObject.AstroConfig`


Library Developers
******************

This module is designed to be expanded by users. The :mod:`AstroObject.AstroObjectBase` module provides basic abstract classes with source code which can be used to create sub-classes with specific functionality (see :ref:`AstroObjectAPI`). By implementing their own ``frame``, users can create Objects (using the :class:`AstroObjectBase.BaseObject` class, and the keyword ``dataClasses``) to make their own data reduction systems.

Example
*******

Here is a simple example use for this module::
    
    >>> obj = ImageObject()
    >>> obj.loadFromFile("Picture.jpg")
    >>> obj.show()
    # Matplotlib Image Plot
    >>> Image = obj.data()
    >>> ScaledImage = np.sqrt(Image)
    >>> obj.save(ScaledImage,"Scaled Image")
    >>> obj.show()
    # Matplotlib Image Plot
    >>> obj.list()
    ["Picture.jpg","Scaled Image"]
    >>> obj.select("Picture.jpg")
    