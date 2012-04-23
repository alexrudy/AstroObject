.. _IRAFToolsWalkthough:

Walkthrough of a basic :mod:`~AstroObject.iraftools` script
===========================================================

The full script we will use is shown below. This example will walk through every part of the script, line by line, to demonstrate the use of :mod:`~AstroObject.iraftools` with :mod:`AstroObject`. In order for this example to make sense, we must assume that certain data files exist:

- ``data.fits``: This is our data file. It should be a pretty picture.
- ``bias.fits``: The bias measurement. The header ``IMAGETYP`` should be ``zero``.
- ``dark.fits``: The dark current measurement. The header ``IMAGETYP`` should be ``dark``.
- ``flat.fits``: The flat field. The header ``IMAGETYP`` should be ``flat``.

.. literalinclude:: /../../Examples/iraf-simple.py

To start the program, we import our **stack** of choice. If you need help understanding **stacks** and **frames**, the basic units for :mod:`AstroObject`, see :ref:`Introduction`. Immediately after importing :mod:`~AstroObject.AstroImage`, we import :func:`UseIRAFTools` from :mod:`~AstroObject.iraftools`. This helper function takes a single argument, a **stack** class, and returns a copy of that **stack** class which can be used with :mod:`~AstroObject.iraftools`. To use :mod:`~AstroObject.iraftools`, we call :func:`UseIRAFTools` on our :class:`~AstroObject.AstroImage.ImageStack`. This function returns a new class for us to use, which for clarity's sake, we will call :class:`~AstroObject.AstroImage.ImageStack`, so that we can't use the non-:mod:`~AstroObject.iraftools` :class:`~AstroObject.AstroImage.ImageStack`.
::
	
	from AstroObject.AstroImage import ImageStack
	from AstroObject.iraftools import UseIRAFTools
	ImageStack = UseIRAFTools(ImageStack) # Enable IRAFTools
	

Next, we import the desired IRAF modules that we want to work with. In this case, we are reducing CCD data, so ``imred`` and ``ccdred`` are appropriate.
::
	
	from pyraf import iraf
	from pyraf.iraf import imred, ccdred
	
Now our environment is all set up. It is time to load some data. We get our data from the FITS files described in the first paragraph. Each one is loaded into the same **stack**. This is fine, since a single stack can hold many **frames**, where each **frame** is a different image.
::
	
	Data = ImageStack.fromFile("data.fits")
	Data.read("bias.fits")
	Data.read("dark.fits")
	Data.read("flat.fits")
	
The first call, to :meth:`ImageStack.fromFile <AstroObject.AstroImage.ImageStack.fromFile>`, simply uses a factory function to replace initializing our :class:`~AstroObject.AstroImage.ImageStack`. This call is the same as::
	
	Data = ImageStack()
	Data.read("data.fits")
	
After loading our data, we want to select the **frame** that we are most likely to use, so that it becomes the frame used by default.
::
	
	Data.select("data")
	
Notice that when we select the frame, we use ``"data"``. The :class:`~AstroObject.AstroImage.ImageStack` class will automtacially remove the ``".fits"`` extension, and use the base of the filename as the statename for imported frames. We could have specified a name for this **frame** using the ``statename`` keyword argument to read.
::
	
	Data.read("data.fits",stataename="another name")
	
Now we are ready to make our ``iraf`` call. In interactive mode, we would have used ``epar`` to set parameters for each ``iraf`` call, then made the call. In ``pyraf``, we use keyword arguments to set the parameters of the IRAF call.
::
  
	iraf.ccdproc(
	    Data.iraf.modatfile("data",append="-reduced"),
	    flat = Data.iraf.infile("flat"),
	    dark = Data.iraf.infile("dark"),
	    zero = Data.iraf.infile("bias"),
	    ccdtype = "",
	    fixpix = "no",
	    overscan = "no",
	    trim = "no",
	    zerocor = "yes",
	    darkcor = "yes",
	    flatcor = "yes",
	)
	
Many of these keyword arguments we have specified explicitly on the command line. However, we can't specify the names of FITS files on the command line, as we don't want to use actual filse, we want to use the data we loaded into our program. First, we needed an @list as input to the ``ccdproc`` function. An @list is a file which has a filename on each line. ``iraf`` then reads the @list and runs the command on each file in the list (or sometimes all files in the list at once). Since we don't want to write out a new list file every time we work with @lists, :mod:`~AstroObject.iraftools` provides a simple interface to creating @lists from data **stacks**. Lets examine this call closely.
::
	
  Data.iraf.modatfile("data",append="-reduced")
	

The function :meth:`iraf.modatfile <AstroObject.iraftools.IRAFTools.modatfile>` creates an @-list which points to FITS files for each of the included states. You can list as many states as you wish as the first arguments to :meth:`iraf.modatfile <AstroObject.iraftools.IRAFToolsMixin.iraf.modatfile>`. Providing no states will generate an @-list which points to all avaialbe states. This is similar to the way :meth:`iraf.inatfile <AstroObject.iraftools.IRAFToolsMixin.iraf.inatfile>` works. Once you call this function, temporary FITS files are generated for each state (in this case, just the ``data`` **frame**) requested. A list of these filenames is then placed in an @list, and the name of that @list is returned from the fucntion, with the "@" already appended to the beginning of the name, making it suitable input for ``iraf``.

Behind the scenes, the call::
  
  Data.iraf.modatfile("data",append="-reduced")
  
created the following files (each filename begins with a temporary directory that looks something like ``/var/folders/7c/_l4kwbx519980p4pdl0q76vc0000gq/T/``, but is your operating-system's temporary file directory. I'll abbreviate that as ``/tmp/``. As well, each time :mod:`~AstroObject.iraftools` provides a file set, it uses a new temporary directory, yours will be different from the example ``tmpa5sRZc``):

- ``/tmp/tmpa5sRZc/dataf9T55J.fits`` which is the FITS file for your data. Notice that the filename begins with your **frame** label, ``data``, and ends with ``.fits``, but has some random characters in it, as well as being placed in a random directory. The :mod:`tempfile` mechanism provided by python ensures that these files will never collide.
- ``/tmp/tmpa5sRZc/tmpxP5JTy.list`` which is a list of the FITS files that it just created. In this case, the file will contain one line::
  
  /tmp/tmpa5sRZc/dataf9T55J.fits
  

When you call :meth:`iraf.done <AstroObject.iraftools.IRAFToolsMixin.iraf.done>`, :mod:`~AstroObject.iraftools` knows to reload ``/tmp/tmpa5sRZc/dataf9T55J.fits`` into the ``Data`` **stack**, and to append the name ``-reduced`` to the label ``data``, so that the new label becomes ``data-reduced``. The FITS file (and, in fact, the whole directory) will be removed at the end of the cleanup process.

There are three styles of file that can be created from :mod:`~AstroObject.iraftools`, input (or ``in``) files, output (or ``out``) files, and modify-in-place, or ``mod`` files. These files can be created individually, or in @lists using various :mod:`~AstroObject.iraftools` methods. These types are documented at :ref:`IRAFTools_Filetypes`.

Along with our @list, created by ``Data.iraf.modatfile("data",append="-reduced")``, we need to provide a flat, dark and bias file as input to the ``ccdproc`` function. These three files we will make with the :meth:`iraf.infile <AstroObject.iraftools.IRAFToolsMixin.iraf.infile>`. Input files are written instantly, and cleaned up automatically by :mod:`~AstroObject.iraftools`, but changes made to these files are not reloaded into the data **stack**. We use these functions to set the appropriate keyword arguments for ``iraf``.
::
  
  flat = Data.iraf.infile("flat"),
  dark = Data.iraf.infile("dark"),
  zero = Data.iraf.infile("bias"),
  

Just like :meth:`iraf.modatfile <AstroObject.iraftools.IRAFToolsMixin.iraf.modatfile>` created temporary FITS files, :meth:`iraf.infile <AstroObject.iraftools.IRAFToolsMixin.iraf.infile>` will create a temporary FITS file for each of those frames. That temporary FITS file will be removed (along with the temporary directory).

The remaining keyword arguments that we provided to ``ccdproc`` are standard ``iraf`` keywords. They obviously depend on what you want to get done with this system.

Once we finish with the ``ccdproc`` command, we need to tell :mod:`~AstroObject.iraftools` that we are done calling ``iraf`` and using these temporary files. Calling :meth:`iraf.done <AstroObject.iraftools.IRAFToolsMixin.iraf.done>` does just that. Specifically, :meth:`iraf.done <AstroObject.iraftools.IRAFToolsMixin.iraf.done>` does the following:

- Reloads any modified files (as created by :meth:`iraf.modfile <AstroObject.iraftools.IRAFToolsMixin.iraf.modfile>` and :meth:`iraf.modatfile <AstroObject.iraftools.IRAFToolsMixin.iraf.modatfile>`).
- Loads any created output files (as set up by :meth:`iraf.outfile <AstroObject.iraftools.IRAFToolsMixin.iraf.outfile>` and :meth:`iraf.outatfile <AstroObject.iraftools.IRAFToolsMixin.iraf.outatfile>`)
- Deletes all of the temporary FITS files that we created.

So the last call in our ``iraf`` command is::
  
  Data.iraf.done()
  

Finally, we want to write our newly-reduced image to a FITS file. :mod:`AstroObject.AstroImage` makes this easy::
  
  Data.write(states=["data-reduced"],filename="final.fits",clobber=True)
  

The ``states=["data-reduced"]`` keyword provides a list of the states that we want to use when writing the FITS file. In this case, we want only the reduced data, so we provide a one-element list of just that **frame** name. ``clobber=True`` tells the module that it is okay to over-write the ``final.fits`` file. By default, trying to overwrite a file will cause an IOError.  

.. _IRAFToolsExample:

An Example :mod:`~AstroObject.iraftools` program
================================================

.. literalinclude:: /../../Examples/iraf.py
    
