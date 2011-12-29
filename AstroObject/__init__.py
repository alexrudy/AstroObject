# 
#  __init__.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.7
#  
 
import logging,time,sys,os


__version__ = '0.2.7'

__all__ = ['AnalyticSpectra','AstroImage','AstroObjectBase','AstroSpectra','Utilities']


logfolder = "Logs/"
filename = __name__+"-"+time.strftime("%Y-%m-%d")
longFormat = "%(asctime)s : %(levelname)-8s : %(name)-40s : %(message)s"
shortFormat = '%(levelname)-8s: %(message)s'
dateFormat = "%Y-%m-%d-%H:%M:%S"

initLOG = logging.getLogger(__name__)
initLOG.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
consoleFormatter = logging.Formatter(shortFormat,datefmt=dateFormat)
console.setFormatter(consoleFormatter)
initLOG.addHandler(console)

if os.access(logfolder,os.F_OK):
    logfile = logging.FileHandler(filename=logfolder+filename+".log",mode="a")
    logfile.setLevel(logging.DEBUG)
    fileformatter = logging.Formatter(longFormat,datefmt=dateFormat)
    logfile.setFormatter(fileformatter)
    initLOG.addHandler(logfile)
    initLOG.removeHandler(console)


def set_log_file(filename):
    """Set the log file"""
    logfile = logging.FileHandler(filename=logfolder+filename+".log",mode="a")
    logfile.setLevel(logging.DEBUG)
    fileformatter = logging.Formatter(longFormat,datefmt=dateFormat)
    logfile.setFormatter(fileformatter)
    initLOG.addHandler(logfile)
    initLOG.removeHandler(console)
    

initLOG.info("Loaded the model %s, called command %s" % (__name__,sys.argv[0]))

