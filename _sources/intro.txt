Introduction to :mod:`AstroObject`
==================================

Welcome to AstroObject, a library for managing Astronomical Data. The idea behind this library is to bring Astronomical data and data reduction into the object-oriented age. This library is not meant for use with what astronomers lovingly call "codes", but rather is designed with full fledged programs in mind.

With that in mind, it is good to know that this module is based around two concepts, Objects and Frames. 

Often, when doing data reduction, you end up manipulating the same image or spectra many times. This process (in my experience) has led me to litter my directories with numerous FITS files, always prepending or appending ``b`` or some other character to indicate the current state of the image. This module allows you to think of each of those states of the same image as a "frame", all belonging to the same "image" object.

It just so happens that the FITS data format supports this understanding as well, by way of FITS extensions. As such, you can store your beautifully reduced science image in the front of a FITS image, but include a full history of that image in subsequent FITS extension frames.

Frames
******

A frame is a single instance of data. It doesn't have to be image data, it could instead be spectral data, or any other data you could think of. The point is that a frame is just one instance of such data. Each frame in :mod:`AstroObject` has a label, and each frame can carry its own data as well as its own metadata.

The format of data in a frame depends on what type of frame you want to use. For the simple :mod:`AstroImage` implementation, a frame is a two-dimensional array of numpy data (along with a stack of other meta-data that it gets to carry around). You should really only write to a frame once (although sometimes you may need a place to put an image temporarily, and then wish to over-write it or delete it later... that is perfectly fine, see CLOBBER), and then that frame will preserve the image data for you.

The :mod:`AstroObject` module comes with a variety of frames, but it is easy to create your own. The required functions for each frame are documented in :ref:`AstroObjectAPI`, and a template class is provided in :class:`AstroObjectBase.FITSFrame`

Object
******

Objects are really just collections of frames with a few additional helpful features. When you reduce an image, you really only care about a single image, and most of the time, you want the most recent changes to that image. That is where objects help. Instead of storing innumerable FITS files, you just add each frame (image) to a single object. Then, you can use that object's methods to easily retrieve and store new data.

Objects provide smart :meth:`save` methods which allow you to pass either an already instantiated :meth:`frame` or just the raw data you wish to store. Then, to retrieve your data, you can ask an object for the :meth:`frame` or the raw data. All of these methods are documented at :class:`AstroObjectBase.FITSObject`.

Expansion
*********

This module is designed to be expanded by users. The :mod:`AstroObjectBase` module provides basic abstract classes with source code which can be used to create sub-classes with specific functionality. By implementing their own ``frame``, users can create Objects (using the :class:`AstroObjectBase.FITSObject` class, and ``dataClasses``) to make their own data reduction systems.

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
    