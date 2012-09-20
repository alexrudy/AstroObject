# -*- coding: utf-8 -*-
# This example assumes that the following files exist:
#  - data.fits
#  - bias.fits (IMAGTYP=zero)
#  - dark.fits (IMAGTYP=dark)
#  - flat.fits (IMAGTYP=flat)
from AstroObject.image import ImageStack
from AstroObject.iraftools import UseIRAFTools
ImageStack = UseIRAFTools(ImageStack) # Enable IRAFTools
from pyraf import iraf
from pyraf.iraf import imred, ccdred
Data = ImageStack.fromFile("data.fits")
Data.read("bias.fits")
Data.read("dark.fits")
Data.read("flat.fits")
Data.select("data")
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
Data.iraf.done()
Data.write(frames=["data-reduced"],filename="final.fits",clobber=True)
