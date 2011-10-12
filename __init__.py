# 
#  __init__.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 
import logging,time,sys,os


logfolder = "Logs/"
filename = "AstroObject-"+time.strftime("%Y-%m-%d")+".log"
longFormat = "%(asctime)s : %(levelname)-8s : %(name)-20s : %(message)s"
shortFormat = '%(levelname)-8s: %(name)-20s: %(message)s'
dateFormat = "%Y-%m-%d-%H:%M:%S"

initLOG = logging.getLogger('')
initLOG.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
consoleFormatter = logging.Formatter(shortFormat,datefmt=dateFormat)
console.setFormatter(consoleFormatter)
initLOG.addHandler(console)

if os.access(logfolder,os.F_OK):
    logfile = logging.FileHandler(filename=logfolder+filename,mode="w")
    logfile.setLevel(logging.DEBUG)
    fileformatter = logging.Formatter(longFormat,datefmt=dateFormat)
    logfile.setFormatter(fileformatter)
    initLOG.addHandler(logfile)

initLOG.info("Launching %s from the %s module" % (sys.argv[0],__name__))