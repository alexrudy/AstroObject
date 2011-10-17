# 
#  __init__.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.0.0
#  
 
import logging,time,sys,os


__version__ = '0.0.0'

logfolder = "Logs/"
filename = "AstroObject-"+time.strftime("%Y-%m-%d")
longFormat = "%(asctime)s : %(levelname)-8s : %(name)-20s : %(message)s"
shortFormat = '%(levelname)-8s: %(message)s'
dateFormat = "%Y-%m-%d-%H:%M:%S"

initLOG = logging.getLogger('')
initLOG.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
consoleFormatter = logging.Formatter(shortFormat,datefmt=dateFormat)
console.setFormatter(consoleFormatter)
initLOG.addHandler(console)

if os.access(logfolder,os.F_OK):
    logfile = logging.FileHandler(filename=logfolder+filename+".log",mode="w")
    logfile.setLevel(logging.DEBUG)
    fileformatter = logging.Formatter(longFormat,datefmt=dateFormat)
    logfile.setFormatter(fileformatter)
    initLOG.addHandler(logfile)


initLOG.info("Launching %s from the %s module" % (sys.argv[0],__name__))
