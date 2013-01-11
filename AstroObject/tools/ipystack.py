# -*- coding: utf-8 -*-
# 
#  ipystack.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2013-01-08.
#  Copyright 2013 Alexander Rudy. All rights reserved.
# 
"""
:mod:`~AstroObject.tools.ipystack` - iPython script integration
===============================================================

"""

from pyshell.base import CLIEngine
from AstroObject.image import ImageStack
from AstroObject.iraftools import UseIRAFTools
ImageStack = UseIRAFTools(ImageStack)


class IPyStack(CLIEngine):
    """Launch iPython with a stack loaded from filenames."""
    
    module = __name__
    
    description = "Launch iPython with an AstroObject image stack."
    
    defaultcfg = False
    
    def __init__(self):
        super(IPyStack, self).__init__()
        
    def parse(self):
        """Parse arguments"""
        self.parser.add_argument('files',default=[],nargs='+',metavar="img.fits",help="Files to load into iPython stack.")
        super(IPyStack, self).parse()
        
    
    def start(self):
        """Parse and load argument."""
        self.stack = ImageStack()
        for filename in self.opts.files:
            self.stack.read(filename,framename=filename,clobber=True)
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        self.shell = InteractiveShellEmbed(banner1="Starting IPython Interpreter with a stack.\n"\
        "'stack' = %r" % self.stack.list())
        
    def do(self):
        """Use the ipython shell!"""
        stack = self.stack
        self.shell()
        
    def end(self):
        """End the process"""
        pass
        
    def kill(self):
        """Kill the process"""
        pass